# Adapted from
# https://github.com/xxyzz/WordDumb/blob/097dd6c1651fdc08b472e0bf639aec444b6e14ec/custom_lemmas.py#L398C1-L438C46

from qgis.gui import QgsFileWidget
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
                    QgsFileWidget.GetFile
                    if config.get("get_file_mode")
                    else QgsFileWidget.GetDirectory
                )

                if widget.storageMode() == QgsFileWidget.GetFile:
                    widget.setDialogTitle(config.get("title", "Select an existing file"))
                    widget.setFilter(config.get("filter", ""))
                else:
                    widget.setDialogTitle(config.get("title", "Select an existing folder"))

                widget.fileChanged.connect(self.commit_and_close_editor)
                return widget

        return QStyledItemDelegate.createEditor(self, parent, option, index)

    def commit_and_close_editor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor)

    def setEditorData(self, editor, index):
        if ServiceConfigModel.is_custom_widget_cell(index):
            widget_type = index.data(Qt.ItemDataRole.UserRole)["custom_type"]
            value = index.data(Qt.ItemDataRole.DisplayRole)

            if widget_type == WidgetTypeEnum.COMBOBOX:
                editor.setCurrentText(value)
            elif widget_type == WidgetTypeEnum.FILEWIDGET:
                editor.setFilePath(value)
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

            model.setData(index, value, Qt.ItemDataRole.EditRole)
        else:
            QStyledItemDelegate.setModelData(self, editor, model, index)
