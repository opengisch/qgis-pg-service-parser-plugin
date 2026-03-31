# Development

## pgserviceparser library

This plugin uses the [pgserviceparser](https://github.com/opengisch/pgserviceparser) library, available as a standalone package on [PyPI](https://pypi.org/project/pgserviceparser/).

## Code style

Use [pre-commit](https://pre-commit.com/) to ensure consistent formatting:

```bash
pip install pre-commit
pre-commit install
```

## Code contributions

We welcome any code contribution — just open a PR.

If the PR deals with GUI changes, add a screenshot or screencast showing the new functionality.

## Generate documentation screenshots

Screenshots for the documentation are generated automatically using a script that drives the plugin inside a QGIS Docker container:

```bash
./scripts/screenshots.sh
```

The script uses a pixel-diffing guard: screenshots are only written to disk if they actually differ from the existing ones, avoiding unnecessary git history pollution.
