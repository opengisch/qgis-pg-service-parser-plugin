from pg_service_parser.conf.enums import SslModeEnum

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
    "sslmode": {
        "default": SslModeEnum.PREFER.value,
        "description": "This option determines whether or with what priority a secure SSL TCP/IP connection will be negotiated with the server.",
        "values": SslModeEnum,
    },
    "passfile": {
        "default": "",
        "description": "Specifies the name of the file used to store passwords.",
    },
}

# Settings to initialize new files
SETTINGS_TEMPLATE = {
    "host": "localhost",
    "port": "5432",
    "dbname": "test",
}
