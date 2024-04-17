[![Release](https://img.shields.io/github/v/release/opengisch/qgis-pg-service-parser-plugin.svg)](https://github.com/opengisch/qgis-pg-service-parser-plugin/releases)

# PG service parser plugin

<img src="https://raw.githubusercontent.com/opengisch/qgis-pg-service-parser-plugin/main/pg_service_parser/images/logo.png" alt="Logo" width="200px" align="left"/>


QGIS v3 plugin to view, edit or copy PG service (i.e., `pg_service.conf`) entries for PostgreSQL connections.

This plugin is distributed under the [GNU GPL v3 license](https://github.com/opengisch/qgis-pg-service-parser-plugin/blob/main/LICENSE).



### pg_service.conf location

Before using the plugin, make sure you've set the `PGSERVICEFILE` environment variable pointing to the `pg_service.conf` file path.



### Edit PG service entries

<img src="https://raw.githubusercontent.com/opengisch/qgis-pg-service-parser-plugin/main/images/edit_service.png" alt="Edit service"/>



### Copy PG service entries

<img src="https://raw.githubusercontent.com/opengisch/qgis-pg-service-parser-plugin/main/images/copy_service.png" alt="Copy service"/>



### For devs

#### pgserviceparser library

This plugin uses the [pgserviceparser](https://github.com/opengisch/pgserviceparser) library. It's also available as a [PYPI package](https://pypi.org/project/pgserviceparser/).



#### Code style

Use pre-commit:

```
pip install pre-commit
pre-commit install
```
