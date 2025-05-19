from qgis.PyQt.QtCore import QAbstractTableModel, QModelIndex, QObject, Qt

from pg_service_parser.core.plugin_settings import PluginSettings


class Shortcut:
    def __init__(self, service_from: str, service_to: str, name: str = None):
        if name:
            self.name = name
        else:
            self.name = f"{service_from} -> {service_to}"
        self.service_from = service_from
        self.service_to = service_to

    def save(self):
        PluginSettings().shortcut_from.setValue(self.service_from, self.name)
        PluginSettings().shortcut_to.setValue(self.service_to, self.name)

    def rename(self, name: str):
        PluginSettings().shortcuts_node.deleteItem(self.name)
        self.name = name
        self.save()

    def delete(self):
        PluginSettings().shortcuts_node.deleteItem(self.name)


class ShortcutsModel(QAbstractTableModel):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.shortcuts = []

        for shortcut in PluginSettings().shortcuts_node.items():
            sh_from = PluginSettings().shortcut_from.value(shortcut)
            sh_to = PluginSettings().shortcut_to.value(shortcut)
            self.shortcuts.append(Shortcut(sh_from, sh_to, shortcut))

    def add_shortcut(self, service_from: str, service_to: str):
        existing_names = [sh.name for sh in self.shortcuts]
        base_name = f"{service_from} -> {service_to}"
        name = base_name
        i = 2
        while name in existing_names:
            name = f"{base_name} ({i})"
            i += 1

        shortcut = Shortcut(service_from, service_to, name)
        shortcut.save()
        row = self.rowCount()
        self.beginInsertRows(QModelIndex(), row, row)
        self.shortcuts.append(shortcut)
        self.endInsertRows()
        self.dataChanged.emit(self.index(row, 0), self.index(row, 0))

    def remove_shortcut(self, index: QModelIndex):
        if not index.isValid():
            return

        self.beginRemoveRows(QModelIndex(), index.row(), index.row())
        self.shortcuts[index.row()].delete()
        del self.shortcuts[index.row()]
        self.endRemoveRows()
        self.dataChanged.emit(index, index)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Vertical:
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            if section == 0:
                return self.tr("Name")
            if section == 1:
                return self.tr("From")
            if section == 2:
                return self.tr("To")

        return super().headerData(section, orientation, role)

    def rowCount(self, parent=QModelIndex()):
        return len(self.shortcuts)

    def columnCount(self, parent=QModelIndex()):
        return 3

    def flags(self, index):
        if not index.isValid():
            return None

        if index.column() == 0:
            return (
                Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsEditable
            )
        else:
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid:
            return None

        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            if index.column() == 0:
                return self.shortcuts[index.row()].name
            if index.column() == 1:
                return self.shortcuts[index.row()].service_from
            if index.column() == 2:
                return self.shortcuts[index.row()].service_to

        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False

        if role == Qt.ItemDataRole.EditRole and len(value) > 0:
            for sh in self.shortcuts:
                if sh.name == value:
                    return False
            if index.column() == 0:
                self.shortcuts[index.row()].rename(value)
                self.dataChanged.emit(index, index)
                return True

        return False
