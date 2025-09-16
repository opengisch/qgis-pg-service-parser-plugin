[![Release](https://img.shields.io/github/v/release/opengisch/qgis-pg-service-parser-plugin.svg)](https://github.com/opengisch/qgis-pg-service-parser-plugin/releases)

# PG service parser plugin

<img src="https://raw.githubusercontent.com/opengisch/qgis-pg-service-parser-plugin/main/pg_service_parser/images/logo.png" alt="Logo" width="200px"/>


QGIS v3 plugin to view, edit or copy PG service (i.e., `pg_service.conf`) entries for PostgreSQL connections.

This plugin is distributed under the [GNU GPL v3 license](https://github.com/opengisch/qgis-pg-service-parser-plugin/blob/main/LICENSE).


### Create a pg_service.conf file

If you don't have a `pg_service.conf` file, the plugin allows you to create one at a default location.

<img width="603" height="133" alt="image" src="https://github.com/user-attachments/assets/fdd6a551-12e3-456d-b116-16fe29a23aa7" />


### pg_service.conf location

If your `pg_service.conf` file is located at `/home/YOUR_USER/.pg_service.conf` (on Linux) or at `%APPDATA%\postgresql\.pg_service.conf` (on Windows), then you are done! The plugin will read your file directly.

If that's not the case, i.e., if your `pg_service.conf` file is not in the aforementioned locations, you can still set the `PGSERVICEFILE` environment variable pointing to your `pg_service.conf` file path before using the plugin.

Clients like QGIS will directly read your `pg_service.conf` file from any of these locations and you'll be able to use any service from this file in the `New Connection` dialog (see [QGIS docs](https://docs.qgis.org/latest/en/docs/user_manual/managing_data_source/opening_data.html#creating-a-stored-connection)).

### Edit PG service entries

<img width="560" height="422" alt="image" src="https://github.com/user-attachments/assets/50629923-8684-4da9-b6dd-1a2797701dfe" />

### Duplicate PG service entries

If you want to duplicate a service, choose whether to copy/clone the service into a new service or to overwrite an existing one.

<img width="560" height="446" alt="image" src="https://github.com/user-attachments/assets/a6120c41-c0fd-45e6-a41e-7b7cc72a57c0" />

If you perform the **overwrite** operation on a regular basis (e.g., switching from a service definition to another, while preserving the name), you can add `Shortcuts`, which give you a handy way to execute the same overwrite from the plugin icon or from the `Database` menu.

<img width="377" height="168" alt="image" src="https://github.com/user-attachments/assets/ce2e8415-b231-46bc-aa38-d1625c4282ac" />

### QGIS Connection to a PG service

You can create QGIS connections to a PG database, directly from the PG services that you edit.

<img width="560" height="422" alt="image" src="https://github.com/user-attachments/assets/4d1a9d0a-55fa-4bea-a633-2a9b1fe21607" />

### For devs

#### pgserviceparser library

This plugin uses the [pgserviceparser](https://github.com/opengisch/pgserviceparser) library, which is also available as a [PYPI package](https://pypi.org/project/pgserviceparser/).



#### Code style

Use pre-commit:

```
pip install pre-commit
pre-commit install
```
