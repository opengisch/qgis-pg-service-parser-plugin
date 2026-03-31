# Usage

## Edit PG service entries

Open the plugin from the **Database** menu or the toolbar icon. The **Services** tab lets you manage your `pg_service.conf` entries.

You can:

- **Add** a new service
- **Remove** one or multiple services
- **Rename** a service (right-click context menu)
- **Duplicate** a service (right-click context menu)
- **Edit settings** — add, remove, or modify key/value pairs for any service
- **Copy settings** to clipboard in `pg_service.conf` format

<!-- screenshot: edit tab with a service selected -->

### Duplicate PG service entries

To duplicate a service, right-click on it and choose **Duplicate service...**. Enter a target service name: if it already exists, you can overwrite it; otherwise, a new service is created.

<!-- screenshot: duplicate service context menu -->

## Shortcuts

If you perform the same overwrite operation regularly (e.g., switching from one service definition to another while preserving the name), you can add **Shortcuts**. These give you a handy way to execute the same copy from the plugin toolbar button or from the **Database** menu.

<!-- screenshot: shortcuts tab -->

## QGIS Connection to a PG service

The **Connections** tab lets you create QGIS connections to a PostgreSQL database directly from the PG services you manage.

<!-- screenshot: connections tab -->

Once created, the connection will be available in the QGIS Browser as well as in the Data Source Manager, for you to add layers to the project.

## Context actions for PG layers

This plugin adds 3 context actions to PostgreSQL layer context menus:

- **Create PG service from layer connection** — visible if the layer's QGIS connection is not using a PG service.
- **Register layer connection as QGIS connection** — visible if the layer's connection is not yet registered in QGIS (e.g., from a colleague's project).
- **Switch layer to existent PG service** — visible if the layer's QGIS connection is not using a PG service.
