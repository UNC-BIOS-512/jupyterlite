# r-sfemergency25 for emscripten-wasm32

`sfemergency25` (GitHub: hellodata-science/sfemergency25) packages 2025 San
Francisco Fire Department / EMS dispatched-calls data (dataset `sf911`) for
R. It's a data-only package (no compiled code, no dependencies beyond
`r-base`) but isn't published anywhere as a conda package, and isn't on
CRAN — upstream distributes it via GitHub only.

Upstream has no tagged releases, so this recipe pins a specific commit
(`5687785b503a4aab54c87582912b8a18df65233c`, 2026-06-13) for reproducibility.

Built as a `noarch: generic` package (pure R + data, no compiled code, so
one build works for every platform) and published to
https://anaconda.org/chuckpr/r-sfemergency25, which `environment.yml` adds
as a fallback channel. The resulting package is ~13MB (mostly
`sf911.rda`).

To rebuild and re-upload (e.g. to pin a newer upstream commit):

```bash
pixi exec rattler-build build --recipe recipe.yaml --output-dir output
pixi exec rattler-build upload anaconda --owner chuckpr \
  --api-key "$ANACONDA_TOKEN" \
  output/noarch/r-sfemergency25-*.conda
```

Requires `ANACONDA_TOKEN` set to a token with upload access to the
`chuckpr` Anaconda.org account.
