from .pg_service_parser_plugin import PGServiceParserPlugin


def classFactory(iface):
    return PGServiceParserPlugin(iface)
