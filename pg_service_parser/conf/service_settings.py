from qgis.PyQt.QtCore import QCoreApplication

from pg_service_parser.conf.enums import SslModeEnum, WidgetTypeEnum


# Settings available for manual addition
# See https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-PARAMKEYWORDS
def SERVICE_SETTINGS():
    return {
        "host": {
            "default": "localhost",
            "description": QCoreApplication.translate("Plugin", "Name of host to connect to."),
        },
        "port": {
            "default": "5432",
            "description": QCoreApplication.translate(
                "Plugin", "Port number to connect to at the server host."
            ),
        },
        "dbname": {
            "default": "test",
            "description": QCoreApplication.translate("Plugin", "The database name."),
        },
        "user": {
            "default": "",
            "description": QCoreApplication.translate(
                "Plugin", "PostgreSQL user name to connect as."
            ),
        },
        "password": {
            "default": "",
            "description": QCoreApplication.translate(
                "Plugin", "Password to be used if the server demands password authentication."
            ),
        },
        "passfile": {
            "default": "",
            "description": QCoreApplication.translate(
                "Plugin", "Specifies the name of the file used to store passwords."
            ),
            "custom_type": WidgetTypeEnum.FILEWIDGET,
            "config": {
                "get_file_mode": True,  # False for folders
                "filter": QCoreApplication.translate("Plugin", "Password file")
                + " (*.pgpass *.conf)",
                "title": QCoreApplication.translate("Plugin", "Select a .pgpass or .conf file"),
            },
        },
        "sslmode": {
            "default": SslModeEnum.PREFER.value,
            "description": QCoreApplication.translate(
                "Plugin",
                "This option determines whether or with what priority a secure SSL TCP/IP connection will be negotiated with the server.",
            ),
            "custom_type": WidgetTypeEnum.COMBOBOX,
            "config": {"values": [e.value for e in SslModeEnum]},
        },
        "sslrootcert": {
            "default": "",
            "description": QCoreApplication.translate(
                "Plugin",
                "Name of a file containing SSL certificate authority (CA) certificate(s).\nIf the file exists, the server's certificate will be verified to be signed by one of these authorities.",
            ),
            "custom_type": WidgetTypeEnum.FILEWIDGET,
            "config": {
                "get_file_mode": True,  # False for folders
                "filter": QCoreApplication.translate("Plugin", "SSL crt files") + " (*.crt)",
                "title": QCoreApplication.translate(
                    "Plugin", "Select the file pointing to SSL CA certificate(s)"
                ),
            },
        },
        "sslcert": {
            "default": "",
            "description": QCoreApplication.translate(
                "Plugin",
                "Specifies the file name of the client SSL certificate, replacing the default ~/.postgresql/postgresql.crt.\nThis parameter is ignored if an SSL connection is not made.",
            ),
            "custom_type": WidgetTypeEnum.FILEWIDGET,
            "config": {
                "get_file_mode": True,  # False for folders
                "filter": QCoreApplication.translate("Plugin", "SSL crt files") + " (*.crt)",
                "title": QCoreApplication.translate(
                    "Plugin", "Select the client SSL certificate file"
                ),
            },
        },
        "sslkey": {
            "default": "",
            "description": QCoreApplication.translate(
                "Plugin",
                "Specifies the location for the secret key used for the client certificate.\nIt can specify a file name that will be used instead of the default ~/.postgresql/postgresql.key\nThis parameter is ignored if an SSL connection is not made.",
            ),
            "custom_type": WidgetTypeEnum.FILEWIDGET,
            "config": {
                "get_file_mode": True,  # False for folders
                "filter": QCoreApplication.translate("Plugin", "SSL secret key files")
                + " (*.key)",
                "title": QCoreApplication.translate("Plugin", "Select the secret key file"),
            },
        },
    }


# Settings to initialize new files
SETTINGS_TEMPLATE = {
    "host": "localhost",
    "port": "5432",
    "dbname": "test",
}
