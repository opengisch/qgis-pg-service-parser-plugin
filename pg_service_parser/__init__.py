from .pg_service_parser_plugin import PgServiceParserPlugin


def classFactory(iface):
    return PgServiceParserPlugin(iface)
