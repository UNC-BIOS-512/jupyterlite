# JupyterLite repo for BIOS-512

[![lite-badge](https://jupyterlite.rtfd.io/en/latest/_static/badge.svg)](https://unc-bios-512.github.io/jupyterlite)

## Building locally

```bash
# Build
pixi run build

# Serve
pixi run serve
```

## Authoring notebooks locally

To author a notebook locally in an environment that matches what's deployed to the students, run `jupyter lab` within the `author` environment managed by pixi:

```bash
pixi run -e author lab
```

## License

Course materials under `content/` are licensed under
[CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/). See
[LICENSE](LICENSE) for details.
