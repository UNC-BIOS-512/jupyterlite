# r-cowsay for emscripten-wasm32

CRAN's `cowsay` R package (real deps: `crayon`, `rlang`, both already
available for the browser kernel) isn't published anywhere as a
conda package targeting `emscripten-wasm32`, so JupyterLite's xeus-r kernel
can't install it directly. This recipe builds it as a `noarch: generic`
package (pure R, no compiled code, so one build works for every platform)
and publishes it to https://anaconda.org/chuckpr/r-cowsay, which
`environment.yml` adds as a fallback channel.

To rebuild and re-upload (e.g. for a new cowsay release):

```bash
pixi exec rattler-build build --recipe recipe.yaml --output-dir output
pixi exec rattler-build upload anaconda --owner chuckpr \
  --api-key "$ANACONDA_TOKEN" \
  output/noarch/r-cowsay-*.conda
```

Requires `ANACONDA_TOKEN` set to a token with upload access to the
`chuckpr` Anaconda.org account.
