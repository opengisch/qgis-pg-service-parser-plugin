# Adapted from
# https://github.com/xxyzz/WordDumb/blob/097dd6c1651fdc08b472e0bf639aec444b6e14ec/custom_lemmas.py#L398C1-L438C46

from qgis.gui import QgsFileWidget, QgsPasswordLineEdit
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QComboBox, QStyledItemDelegate

from pg_service_parser.conf.enums import WidgetTypeEnum
from pg_service_parser.core.setting_model import ServiceConfigModel


class ServiceConfigDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        if ServiceConfigModel.is_custom_widget_cell(index):
            widget_type = index.data(Qt.ItemDataRole.UserRole)["custom_type"]
            config = index.data(Qt.ItemDataRole.UserRole)["config"]

            if widget_type == WidgetTypeEnum.COMBOBOX:
                options = config["values"]

                widget = QComboBox(parent)
                if isinstance(options, list):
                    for value in options:
                        widget.addItem(value, value)

                widget.currentIndexChanged.connect(self.commit_and_close_editor)
                return widget

            elif widget_type == WidgetTypeEnum.FILEWIDGET:
                widget = QgsFileWidget(parent)
                widget.setStorageMode(
                    QgsFileWidget.StorageMode.GetFile
                    if config.get("get_file_mode")
                    else QgsFileWidget.StorageMode.GetDirectory
                )

                if widget.storageMode() == QgsFileWidget.StorageMode.GetFile:
                    widget.setDialogTitle(config.get("title", self.tr("Select an existing file")))
                    widget.setFilter(config.get("filter", ""))
                else:
                    widget.setDialogTitle(
                        config.get("title", self.tr("Select an existing folder"))
                    )

                widget.fileChanged.connect(self.commit_and_close_editor)
                return widget

            elif widget_type == WidgetTypeEnum.PASSWORD:
                widget = QgsPasswordLineEdit(parent)
                widget.editingFinished.connect(self.commit_and_close_editor)
                return widget

        return QStyledItemDelegate.createEditor(self, parent, option, index)

    def commit_and_close_editor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor)

    def setEditorData(self, editor, index):
        if ServiceConfigModel.is_custom_widget_cell(index):
            widget_type = index.data(Qt.ItemDataRole.UserRole)["custom_type"]
            value = (
                index.data(Qt.ItemDataRole.EditRole)
                if widget_type == WidgetTypeEnum.PASSWORD
                else index.data(Qt.ItemDataRole.DisplayRole)
            )

            if widget_type == WidgetTypeEnum.COMBOBOX:
                editor.setCurrentText(value)
            elif widget_type == WidgetTypeEnum.FILEWIDGET:
                editor.setFilePath(value)
            elif widget_type == WidgetTypeEnum.PASSWORD:
                editor.setText(value)
        else:
            QStyledItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        if ServiceConfigModel.is_custom_widget_cell(index):
            widget_type = index.data(Qt.ItemDataRole.UserRole)["custom_type"]
            value = ""

            if widget_type == WidgetTypeEnum.COMBOBOX:
                value = editor.currentData()
            elif widget_type == WidgetTypeEnum.FILEWIDGET:
                value = editor.filePath()
            elif widget_type == WidgetTypeEnum.PASSWORD:
                value = editor.text()

            model.setData(index, value, Qt.ItemDataRole.EditRole)
        else:
            QStyledItemDelegate.setModelData(self, editor, model, index)


class ShortcutServiceDelegate(QStyledItemDelegate):
    """Delegate that shows a combobox with available services for From/To columns."""

    FROM_COL = 1
    TO_COL = 2

    def __init__(self, service_names_func, parent=None):
        super().__init__(parent)
        self.__service_names_func = service_names_func

    def createEditor(self, parent, option, index):
        if index.column() in (self.FROM_COL, self.TO_COL):
            widget = QComboBox(parent)
            widget.addItems([""] + self.__service_names_func())
            widget.currentIndexChanged.connect(self.__commit_and_close_editor)
            return widget

        return QStyledItemDelegate.createEditor(self, parent, option, index)

    def __commit_and_close_editor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor)

    def setEditorData(self, editor, index):
        if index.column() in (self.FROM_COL, self.TO_COL):
            value = index.data(Qt.ItemDataRole.DisplayRole)
            editor.setCurrentText(value or "")
        else:
            QStyledItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        if index.column() in (self.FROM_COL, self.TO_COL):
            model.setData(index, editor.currentText(), Qt.ItemDataRole.EditRole)
        else:
            QStyledItemDelegate.setModelData(self, editor, model, index)
