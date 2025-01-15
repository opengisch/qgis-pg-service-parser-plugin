from pg_service_parser.conf.enums import SslModeEnum, WidgetTypeEnum

# Settings available for manual addition
# See https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-PARAMKEYWORDS
SERVICE_SETTINGS = {
    "host": {"default": "localhost", "description": "Name of host to connect to."},
    "port": {"default": "5432", "description": "Port number to connect to at the server host."},
    "dbname": {"default": "test", "description": "The database name."},
    "user": {"default": "", "description": "PostgreSQL user name to connect as."},
    "password": {
        "default": "",
        "description": "Password to be used if the server demands password authentication.",
    },
    "passfile": {
        "default": "",
        "description": "Specifies the name of the file used to store passwords.",
        "custom_type": WidgetTypeEnum.FILEWIDGET,
        "config": {
            "get_file_mode": True,  # False for folders
            "filter": "Password file (*.pgpass *.conf)",
            "title": "Select a .pgpass or .conf file",
        },
    },
    "sslmode": {
        "default": SslModeEnum.PREFER.value,
        "description": "This option determines whether or with what priority a secure SSL TCP/IP connection will be negotiated with the server.",
        "custom_type": WidgetTypeEnum.COMBOBOX,
        "config": {"values": [e.value for e in SslModeEnum]},
    },
    "sslrootcert": {
        "default": "",
        "description": "Name of a file containing SSL certificate authority (CA) certificate(s).\nIf the file exists, the server's certificate will be verified to be signed by one of these authorities.",
        "custom_type": WidgetTypeEnum.FILEWIDGET,
        "config": {
            "get_file_mode": True,  # False for folders
            "filter": "SSL crt files (*.crt)",
            "title": "Select the file pointing to SSL CA certificate(s)",
        },
    },
    "sslcert": {
        "default": "",
        "description": "Specifies the file name of the client SSL certificate, replacing the default ~/.postgresql/postgresql.crt.\nThis parameter is ignored if an SSL connection is not made.",
        "custom_type": WidgetTypeEnum.FILEWIDGET,
        "config": {
            "get_file_mode": True,  # False for folders
            "filter": "SSL crt files (*.crt)",
            "title": "Select the client SSL certificate file",
        },
    },
    "sslkey": {
        "default": "",
        "description": "Specifies the location for the secret key used for the client certificate.\nIt can specify a file name that will be used instead of the default ~/.postgresql/postgresql.key\nThis parameter is ignored if an SSL connection is not made.",
        "custom_type": WidgetTypeEnum.FILEWIDGET,
        "config": {
            "get_file_mode": True,  # False for folders
            "filter": "SSL secret key files (*.key)",
            "title": "Select the secret key file",
        },
    },
}

# Settings to initialize new files
SETTINGS_TEMPLATE = {
    "host": "localhost",
    "port": "5432",
    "dbname": "test",
}
