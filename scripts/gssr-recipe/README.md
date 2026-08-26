# r-gssr for emscripten-wasm32

`gssr` (GitHub: kjhealy/gssr) packages the US General Social Survey (GSS)
Cumulative Data File and Panel Data for R. It's a data-only package (no
compiled code) but isn't published anywhere as a conda package, and isn't
even on CRAN — upstream distributes it via R-Universe binaries or
`remotes::install_github()` because of its data size. Neither of those
install paths works for JupyterLite's xeus-r kernel.

Upstream has no tagged releases, so this recipe pins a specific commit
(`769d48c53df87e8c7bc3eecbb0432e92d5684cf1`, 2026-03-12) for reproducibility.

`gssr` Imports `curl` (used only by `gss_get_yr()`/`gss_get_years()` to
download a single year's data live from NORC), but `r-curl` isn't available
for the emscripten-wasm32 target, and a live network download wouldn't work
in the sandboxed browser kernel anyway. `build.sh` strips those two
functions and the `curl` dependency out of `DESCRIPTION`/`NAMESPACE`/`R/`
before building. Everything else — `gss_all`, `gss_sub`,
`gss_panel06_long`, `gss_panel08_long`, `gss_panel10_long`, `gss_panel20`,
and `gss_which_years()` — is untouched.

Built as a `noarch: generic` package (pure R + data, no compiled code, so
one build works for every platform) and published to
https://anaconda.org/chuckpr/r-gssr, which `environment.yml` adds as a
fallback channel. The resulting package is ~30MB (mostly `gss_all.rda`),
noticeably larger than this repo's other custom packages — worth knowing
before adding it to the default kernel environment, since every student's
first kernel launch downloads it.

To rebuild and re-upload (e.g. to pin a newer upstream commit once GSS
publishes new data):

```bash
pixi exec rattler-build build --recipe recipe.yaml --output-dir output
pixi exec rattler-build upload anaconda --owner chuckpr \
  --api-key "$ANACONDA_TOKEN" \
  output/noarch/r-gssr-*.conda
```

Requires `ANACONDA_TOKEN` set to a token with upload access to the
`chuckpr` Anaconda.org account.
