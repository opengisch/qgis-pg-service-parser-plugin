[![Release](https://img.shields.io/github/v/release/opengisch/qgis-pg-service-parser-plugin.svg)](https://github.com/opengisch/qgis-pg-service-parser-plugin/releases)

# PG service parser plugin

<img src="https://raw.githubusercontent.com/opengisch/qgis-pg-service-parser-plugin/main/pg_service_parser/images/logo.png" alt="Logo" width="200px"/>


QGIS v3 plugin to view, edit or copy PG service (i.e., `pg_service.conf`) entries for PostgreSQL connections.

This plugin is distributed under the [GNU GPL v3 license](https://github.com/opengisch/qgis-pg-service-parser-plugin/blob/main/LICENSE).



### pg_service.conf location

If your `pg_service.conf` file is located at `/home/YOUR_USER/.pg_service.conf` (on Linux) or at `%APPDATA%\postgresql\.pg_service.conf` (on Windows), then you are done! The plugin will read your file directly.

If that's not the case, i.e., if your `pg_service.conf` file is not in the aforementioned locations, you can still set the `PGSERVICEFILE` environment variable pointing to your `pg_service.conf` file path before using the plugin.



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
