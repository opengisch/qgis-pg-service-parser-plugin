from qgis.core import (
    QgsAbstractDatabaseProviderConnection,
    QgsDataSourceUri,
    QgsProviderRegistry,
)
from qgis.gui import QgsGui
from qgis.PyQt.QtCore import QSettings


def get_connections(service: str) -> dict[str, QgsAbstractDatabaseProviderConnection]:
    res = {}
    provider = QgsProviderRegistry.instance().providerMetadata("postgres")
    conns = provider.connections()
    for key, pg_conn in conns.items():
        if QgsDataSourceUri(pg_conn.uri()).service() == service:
            res[key] = pg_conn

    return res


def create_connection(service: str, connection_name: str) -> None:
    config = {}
    uri = f"service='{service}'"
    provider = QgsProviderRegistry.instance().providerMetadata("postgres")
    conn = provider.createConnection(uri, config)
    provider.saveConnection(conn, connection_name)
    # conn.store(name)


def remove_connection(connection_name: str) -> None:
    provider = QgsProviderRegistry.instance().providerMetadata("postgres")
    provider.deleteConnection(connection_name)


def edit_connection(connection_name: str) -> None:
    provider = QgsProviderRegistry.instance().providerMetadata("postgres")

    if connection_name in provider.dbConnections():
        pg = QgsGui.sourceSelectProviderRegistry().providerByName("postgres")
        w = pg.createDataSourceWidget()

        settings = QSettings()
        settings.value("PostgreSQL/connections/selected")
        settings.setValue("PostgreSQL/connections/selected", connection_name)

        w.refresh()  # To reflect the newly selected connection
        w.btnEdit_clicked()
