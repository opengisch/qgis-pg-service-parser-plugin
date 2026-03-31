
![logo](./assets/images/logo.png){: style="width:200px"}

# PG Service Parser Plugin

QGIS plugin to **view**, **edit** or **copy** PG service (i.e., `pg_service.conf`) entries for PostgreSQL connections.

This plugin is built on top of [pgserviceparser](https://github.com/opengisch/pgserviceparser), a standalone Python library (available on [PyPI](https://pypi.org/project/pgserviceparser/)) for reading, writing, and managing PostgreSQL service files. The library also provides its own GUI module that can be used independently of QGIS.

## Features

- **Create** a `pg_service.conf` file at the default location if one doesn't exist yet.
- **Edit** PG service entries — add, remove, rename, duplicate services and their settings.
- **Copy settings** between services using shortcuts for frequent overwrite operations.
- **Create QGIS connections** to PostgreSQL databases directly from your PG services.
- **Context actions** for PostgreSQL layers — create services from layer connections, register connections in QGIS, or switch layers to an existing PG service.

## Links

- [GitHub repository](https://github.com/opengisch/qgis-pg-service-parser-plugin)
- [QGIS plugin repository](https://plugins.qgis.org/plugins/pg_service_parser/)
- [pgserviceparser library](https://github.com/opengisch/pgserviceparser)

## License

This plugin is distributed under the [GNU GPL v3 license](https://github.com/opengisch/qgis-pg-service-parser-plugin/blob/main/LICENSE).
