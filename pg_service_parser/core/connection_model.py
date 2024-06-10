from qgis.core import QgsAbstractDatabaseProviderConnection
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

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        key = list(self.__model_data.keys())[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == self.KEY_COL:
                return key
            elif index.column() == self.VALUE_COL:
                return self.__model_data[key].uri()
        elif role == Qt.ItemDataRole.FontRole:
            if index.column() == self.KEY_COL:
                font = QFont()
                font.setBold(True)
                return font
            elif index.column() == self.VALUE_COL:
                font = QFont()
                font.setItalic(True)
                return font

        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.DisplayRole = Qt.DisplayRole
    ):
        if orientation == Qt.Horizontal:
            if section == self.KEY_COL:
                return "Connection name"
            elif section == self.VALUE_COL:
                return "Configuration"

    def flags(self, idx):
        if not idx.isValid():
            return ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEnabled

        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def service_name(self):
        return self.__service_name
