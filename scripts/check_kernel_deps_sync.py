#!/usr/bin/env python3
"""Check that environment.yml and pixi.toml's [feature.author] deps agree.

environment.yml pins the packages that ship in the browser (emscripten-forge
build, plus an experimental `pip:` sub-list for pure-Python packages not on
emscripten-forge/conda-forge). pixi.toml's `author` feature is the native
equivalent used for local authoring with a real Jupyter server: conda deps in
`[feature.author.dependencies]`, pip-only deps in
`[feature.author.pypi-dependencies]`. Package *names* must match between the
two on each side, or a student notebook could work locally but fail (or
differ) in the browser, and vice versa.
"""

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENVIRONMENT_YML = ROOT / "environment.yml"
PIXI_TOML = ROOT / "pixi.toml"

# Packages that only make sense in the local authoring env (e.g. the
# notebook frontend itself) and have no browser-kernel counterpart.
LOCAL_ONLY_EXTRAS = {"jupyterlab"}


def parse_environment_yml_deps(path):
    """Return (conda_deps, pip_deps) from environment.yml's dependencies list."""
    lines = path.read_text().splitlines()
    conda_deps = set()
    pip_deps = set()
    in_deps = False
    in_pip = False
    deps_indent = pip_indent = None
    for line in lines:
        if re.match(r"^dependencies:\s*$", line):
            in_deps = True
            continue
        if not in_deps:
            continue
        if not line.strip():
            continue
        if re.match(r"^\S", line):  # dedent: new top-level key
            break

        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if deps_indent is None:
            deps_indent = indent

        if in_pip and indent <= pip_indent:
            in_pip = False

        if stripped == "- pip:" and indent == deps_indent:
            in_pip = True
            pip_indent = indent
            continue

        m = re.match(r"-\s*([A-Za-z0-9_.\-]+)", stripped)
        if not m:
            continue
        (pip_deps if in_pip else conda_deps).add(m.group(1))
    return conda_deps, pip_deps


def parse_pixi_author_deps(path):
    """Return (conda_deps, pypi_deps) from pixi.toml's author feature."""
    with path.open("rb") as f:
        data = tomllib.load(f)
    author = data.get("feature", {}).get("author", {})
    conda_deps = set(author.get("dependencies", {}).keys())
    pypi_deps = set(author.get("pypi-dependencies", {}).keys())
    return conda_deps, pypi_deps


def diff(label, env_side, pixi_side):
    missing_from_pixi = env_side - pixi_side
    missing_from_env = pixi_side - env_side
    if not missing_from_pixi and not missing_from_env:
        return []
    lines = [f"{label} out of sync:"]
    if missing_from_pixi:
        lines.append(f"  in environment.yml but not pixi.toml author feature: {sorted(missing_from_pixi)}")
    if missing_from_env:
        lines.append(f"  in pixi.toml author feature but not environment.yml: {sorted(missing_from_env)}")
    return lines


def main():
    env_conda, env_pip = parse_environment_yml_deps(ENVIRONMENT_YML)
    pixi_conda, pixi_pypi = parse_pixi_author_deps(PIXI_TOML)
    pixi_conda -= LOCAL_ONLY_EXTRAS

    messages = diff("conda dependencies", env_conda, pixi_conda)
    messages += diff("pip dependencies", env_pip, pixi_pypi)

    if not messages:
        return 0

    print("\n".join(messages))
    print(
        "\nIf this is intentional, add local-only extras to LOCAL_ONLY_EXTRAS "
        "in scripts/check_kernel_deps_sync.py, otherwise update the missing spec."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
