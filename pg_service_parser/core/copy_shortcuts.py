from qgis.PyQt.QtCore import QAbstractTableModel, QModelIndex, QObject, Qt
from qgis.PyQt.QtGui import QColorConstants, QFont

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
    def __init__(self, parent: QObject = None, service_names_func=None):
        super().__init__(parent)
        self.shortcuts = []
        self.__service_names_func = service_names_func

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

    def add_empty_shortcut(self):
        """Add a new empty shortcut row to be filled by the user."""
        row = self.rowCount()
        self.beginInsertRows(QModelIndex(), row, row)
        shortcut = Shortcut("", "", f"new shortcut {row + 1}")
        self.shortcuts.append(shortcut)
        self.endInsertRows()
        return row

    def rename_service(self, old_name: str, new_name: str):
        """Update all shortcuts that reference old_name to use new_name."""
        for row, shortcut in enumerate(self.shortcuts):
            changed = False
            if shortcut.service_from == old_name:
                shortcut.service_from = new_name
                changed = True
            if shortcut.service_to == old_name:
                shortcut.service_to = new_name
                changed = True
            if changed:
                shortcut.rename(f"{shortcut.service_from} -> {shortcut.service_to}")
                shortcut.save()
                self.dataChanged.emit(self.index(row, 0), self.index(row, self.columnCount() - 1))

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

        return (
            Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
        )

    def __is_missing_service(self, service_name):
        """Check if a service name does not exist in available services."""
        if not service_name or not self.__service_names_func:
            return False
        return service_name not in self.__service_names_func()

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

        if index.column() in (1, 2):
            service = (
                self.shortcuts[index.row()].service_from
                if index.column() == 1
                else self.shortcuts[index.row()].service_to
            )
            missing = self.__is_missing_service(service)

            if role == Qt.ItemDataRole.ForegroundRole and missing:
                return QColorConstants.Red

            if role == Qt.ItemDataRole.FontRole and missing:
                font = QFont()
                font.setItalic(True)
                return font

            if role == Qt.ItemDataRole.ToolTipRole and missing:
                return self.tr("Service '{}' does not exist").format(service)

        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False

        if role == Qt.ItemDataRole.EditRole and len(value) > 0:
            if index.column() == 0:
                for sh in self.shortcuts:
                    if sh.name == value:
                        return False
                self.shortcuts[index.row()].rename(value)
                self.dataChanged.emit(index, index)
                return True
            elif index.column() == 1:
                shortcut = self.shortcuts[index.row()]
                shortcut.service_from = value
                # Auto-update name
                shortcut.rename(f"{shortcut.service_from} -> {shortcut.service_to}")
                shortcut.save()
                self.dataChanged.emit(self.index(index.row(), 0), self.index(index.row(), 2))
                return True
            elif index.column() == 2:
                shortcut = self.shortcuts[index.row()]
                shortcut.service_to = value
                # Auto-update name
                shortcut.rename(f"{shortcut.service_from} -> {shortcut.service_to}")
                shortcut.save()
                self.dataChanged.emit(self.index(index.row(), 0), self.index(index.row(), 2))
                return True

        return False
