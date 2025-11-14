from qgis.core import QgsAbstractDatabaseProviderConnection, QgsDataSourceUri
from qgis.PyQt.QtCore import QAbstractTableModel, QModelIndex, Qt
from qgis.PyQt.QtGui import QFont


class ServiceConnectionModel(QAbstractTableModel):
    KEY_COL = 0
    VALUE_COL = 1

    def __init__(
        self, service_name: str, connections: dict[str, QgsAbstractDatabaseProviderConnection]
    ) -> None:
        super().__init__()
        self.__service_name = service_name
        self.__model_data = connections

    def rowCount(self, parent=QModelIndex()):
        return len(self.__model_data)

    def columnCount(self, parent=QModelIndex()):
        return 2

    def index_to_connection_key(self, index):
        return list(self.__model_data.keys())[index.row()]

    def clean_uri(self, uri_string: str) -> str:
        """
        Clean a datasource URI by removing password
        """
        cleaned_uri = QgsDataSourceUri.removePassword(uri_string, True)
        # Awkward, but we must also manually remove the password.
        # In some cases, the method does not work
        uri = QgsDataSourceUri(uri_string)
        cleaned_uri = cleaned_uri.replace(f"password='{uri.password()}'", "password='XXXXXXX'")

        return cleaned_uri

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        key = list(self.__model_data.keys())[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == self.KEY_COL:
                return key
            elif index.column() == self.VALUE_COL:
                return self.clean_uri(self.__model_data[key].uri())
        elif role == Qt.ItemDataRole.FontRole:
            if index.column() == self.KEY_COL:
                font = QFont()
                font.setBold(True)
                return font
            elif index.column() == self.VALUE_COL:
                font = QFont()
                font.setItalic(True)
                return font
        elif role == Qt.ItemDataRole.ToolTipRole:
            if index.column() == self.VALUE_COL:
                return self.clean_uri(self.__model_data[key].uri())

        return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if section == self.KEY_COL:
                return self.tr("Connection name")
            elif section == self.VALUE_COL:
                return self.tr("URI")

        return QAbstractTableModel.headerData(self, section, orientation, role)

    def flags(self, idx):
        if not idx.isValid():
            return ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEnabled

        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def service_name(self):
        return self.__service_name
