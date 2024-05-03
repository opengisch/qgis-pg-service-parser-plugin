from qgis.PyQt.QtCore import QAbstractTableModel, Qt, pyqtSignal
from qgis.PyQt.QtGui import QColorConstants, QFont


class ServiceConfigModel(QAbstractTableModel):
    KEY_COL = 0
    VALUE_COL = 1

    is_dirty_changed = pyqtSignal(bool)  # Whether the model gets dirty or not

    def __init__(self, service_name, service_config):
        super().__init__()
        self.__service_name = service_name
        self.__model_data = service_config
        self.__original_data = service_config.copy()
        self.__dirty = False

    def rowCount(self, parent):
        return len(self.__model_data)

    def columnCount(self, parent):
        return 2

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        key = list(self.__model_data.keys())[index.row()]
        if role == Qt.DisplayRole:
            if index.column() == self.KEY_COL:
                return key
            elif index.column() == self.VALUE_COL:
                return self.__model_data[key]
        elif role == Qt.EditRole and index.column() == self.VALUE_COL:
            return self.__model_data[key]
        elif role == Qt.FontRole:
            if index.column() == self.KEY_COL:
                font = QFont()
                font.setBold(True)
                return font
            elif (
                index.column() == self.VALUE_COL
                and self.__model_data[key] != self.__original_data[key]
            ):
                font = QFont()
                font.setItalic(True)
                return font
        elif role == Qt.ForegroundRole and index.column() == self.VALUE_COL:
            if self.__model_data[key] != self.__original_data[key]:
                return QColorConstants.DarkGreen

        return None

    def setData(self, index, value, role=Qt.EditRole) -> bool:
        if not index.isValid():
            return False

        key = list(self.__model_data.keys())[index.row()]
        if value != self.__model_data[key]:
            self.__model_data[key] = value

            if value != self.__original_data[key]:
                self.__dirty = True
                self.is_dirty_changed.emit(True)
            else:
                if self.__model_data == self.__original_data:
                    self.__dirty = False
                    self.is_dirty_changed.emit(False)

            return True

        return False

    def flags(self, idx):
        if not idx.isValid():
            return ~Qt.ItemIsSelectable & ~Qt.ItemIsEnabled

        _flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if idx.column() == self.KEY_COL:
            return _flags
        elif idx.column() == self.VALUE_COL:
            return _flags | Qt.ItemIsEditable

    def is_dirty(self):
        return self.__dirty

    def service_config(self):
        return self.__model_data.copy()

    def service_name(self):
        return self.__service_name

    def set_not_dirty(self):
        # Data saved in the provider
        self.__original_data = self.__model_data.copy()
        self.__dirty = False
        self.is_dirty_changed.emit(False)
