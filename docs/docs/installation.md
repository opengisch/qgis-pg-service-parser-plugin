# Installation

## Install the plugin

The plugin is available from the official QGIS plugin repository. In QGIS, go to **Plugins > Manage and Install Plugins...** and search for **PG service parser**.

## pg_service.conf location

If your `pg_service.conf` file is located at one of the default locations, the plugin will find it automatically:

- **Linux**: `/home/YOUR_USER/.pg_service.conf`
- **Windows**: `%APPDATA%\postgresql\.pg_service.conf`

If your file is elsewhere, set the `PGSERVICEFILE` environment variable pointing to your file path before opening the plugin.

Clients like QGIS will directly read your `pg_service.conf` file from any of these locations and you'll be able to use any service from this file in the **New Connection** dialog (see [QGIS docs](https://docs.qgis.org/latest/en/docs/user_manual/managing_data_source/opening_data.html#creating-a-stored-connection)).

## Create a pg_service.conf file

If you don't have a `pg_service.conf` file, the plugin allows you to create one at a default location.

<!-- screenshot: service file creation prompt -->
