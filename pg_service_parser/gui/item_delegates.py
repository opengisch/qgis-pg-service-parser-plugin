# Adapted from
# https://github.com/xxyzz/WordDumb/blob/097dd6c1651fdc08b472e0bf639aec444b6e14ec/custom_lemmas.py#L398C1-L438C46

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QComboBox, QStyledItemDelegate

from pg_service_parser.core.item_models import ServiceConfigModel


class ServiceConfigDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        if ServiceConfigModel.is_sslmode_edit_cell(index):
            options = list(index.data(Qt.ItemDataRole.UserRole).values())[0]
            combo_box = QComboBox(parent)
            if isinstance(options, list):
                for value in options:
                    combo_box.addItem(value, value)

            combo_box.currentIndexChanged.connect(self.commit_and_close_editor)

            return combo_box

        return QStyledItemDelegate.createEditor(self, parent, option, index)

    def commit_and_close_editor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor)

    def setEditorData(self, editor, index):
        if ServiceConfigModel.is_sslmode_edit_cell(index):
            value = index.data(Qt.ItemDataRole.DisplayRole)
            editor.setCurrentText(value)
        else:
            QStyledItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        if ServiceConfigModel.is_sslmode_edit_cell(index):
            value = editor.currentData()
            model.setData(index, value, Qt.ItemDataRole.EditRole)
        else:
            QStyledItemDelegate.setModelData(self, editor, model, index)
