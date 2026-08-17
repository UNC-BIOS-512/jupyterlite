#!/usr/bin/env python3
"""Check that environment.yml and pixi.toml's [feature.author] deps agree.

environment.yml pins the packages that ship in the browser (emscripten-forge
build). pixi.toml's `author` feature is the native equivalent used for local
authoring with a real Jupyter server. Package *names* must match between the
two, or a student notebook could work locally but fail (or differ) in the
browser, and vice versa.
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
LOCAL_ONLY_EXTRAS = {"jupyterlab", "jupyterlab_rise"}


def parse_environment_yml_deps(path):
    lines = path.read_text().splitlines()
    deps = set()
    in_deps = False
    for line in lines:
        if re.match(r"^dependencies:\s*$", line):
            in_deps = True
            continue
        if in_deps:
            if re.match(r"^\S", line):  # dedent: new top-level key
                break
            m = re.match(r"^\s*-\s*([A-Za-z0-9_.\-]+)", line)
            if m:
                deps.add(m.group(1))
    return deps


def parse_pixi_author_deps(path):
    with path.open("rb") as f:
        data = tomllib.load(f)
    author_deps = data.get("feature", {}).get("author", {}).get("dependencies", {})
    return set(author_deps.keys())


def main():
    env_deps = parse_environment_yml_deps(ENVIRONMENT_YML)
    pixi_deps = parse_pixi_author_deps(PIXI_TOML) - LOCAL_ONLY_EXTRAS

    missing_from_pixi = env_deps - pixi_deps
    missing_from_env = pixi_deps - env_deps

    if not missing_from_pixi and not missing_from_env:
        return 0

    print("environment.yml and pixi.toml [feature.author.dependencies] are out of sync:")
    if missing_from_pixi:
        print(f"  in environment.yml but not pixi.toml author feature: {sorted(missing_from_pixi)}")
    if missing_from_env:
        print(f"  in pixi.toml author feature but not environment.yml: {sorted(missing_from_env)}")
    print(
        "\nIf this is intentional, add local-only extras to LOCAL_ONLY_EXTRAS "
        "in scripts/check_kernel_deps_sync.py, otherwise update the missing spec."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
