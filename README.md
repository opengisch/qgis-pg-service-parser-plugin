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

<img width="566" height="429" alt="image" src="https://github.com/user-attachments/assets/1af6ef30-2270-4b5e-9523-1584ffdf80d2" />


### Duplicate PG service entries

If you want to duplicate a service, choose a source service and then enter a target service name. If the target service name already exists, you can overwrite it with the same settings of the source one. Otherwise, a new service will be created.

<img width="566" height="457" alt="image" src="https://github.com/user-attachments/assets/d3475562-f593-44f3-b582-0a6179f6e458" />

If you perform the **overwrite** operation on a regular basis (e.g., switching from a service definition to another, while preserving the name), you can add `Shortcuts`, which give you a handy way to execute the same overwrite from the plugin icon or from the `Database` menu.

<img width="377" height="168" alt="image" src="https://github.com/user-attachments/assets/ce2e8415-b231-46bc-aa38-d1625c4282ac" />

### QGIS Connection to a PG service

You can create QGIS connections to a PG database, directly from the PG services that you edit.

<img width="566" height="429" alt="image" src="https://github.com/user-attachments/assets/eaccb586-fb66-47e2-94b3-51b89d673db5" />

Once created, the connection will be available in the QGIS Browser as well as in the Data Source Manager, for you to add layers to the project.

<img width="285" height="248" alt="image" src="https://github.com/user-attachments/assets/76cedc78-1884-4f86-8d0d-74dac321be17" />

### Context actions for PG layers

This plugin adds 3 new context actions to the layer's context menu:

<img width="590" height="382" alt="image" src="https://github.com/user-attachments/assets/695abfbe-02da-45f1-8168-999fd5faaa53" />


  + **Create PG service from layer connection**
    
    Visible if the layer is a PostgreSQL layer and its QGIS connection is not using a PG service.
    
  + **Register layer connection as QGIS connection**
    
    Visible if the layer is a PostgreSQL layer and its connection to PostgreSQL is not yet registered in QGIS (e.g., could come from a project of one of your colleagues).
    
  + **Switch layer to existent PG service**
    
    Visible if the layer is a PostgreSQL layer and its QGIS connection is not using a PG service.

### For devs

#### pgserviceparser library

This plugin uses the [pgserviceparser](https://github.com/opengisch/pgserviceparser) library, which is available as a standalone package on [PYPI](https://pypi.org/project/pgserviceparser/).


#### Code style

Use pre-commit:

```
pip install pre-commit
pre-commit install
```

#### Code contributions

We welcome any code contribution, just open a PR.
If the PR deals with GUI changes, add a screenshot/screencast showing off the new functionality.
