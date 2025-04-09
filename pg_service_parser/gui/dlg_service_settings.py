from qgis.PyQt.QtCore import Qt, pyqtSlot
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QListWidgetItem

from pg_service_parser.conf.service_settings import SERVICE_SETTINGS
from pg_service_parser.utils import get_ui_class

DIALOG_UI = get_ui_class("service_settings_dialog.ui")


class ServiceSettingsDialog(QDialog, DIALOG_UI):

    def __init__(self, parent, used_settings: list[str]):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.lstSettings.itemSelectionChanged.connect(self.__selection_changed)
        self.buttonBox.accepted.connect(self.__accepted)

        self.__selection_changed()  # Initialize button status

        # Load data
        for setting, data in SERVICE_SETTINGS.items():
            item = QListWidgetItem(setting)
            if setting in used_settings:
                item.setFlags(
                    item.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEnabled
                )
            if data.get("description", None):
                item.setToolTip(data["description"])

            self.lstSettings.addItem(item)

        self.settings_to_add = []

    @pyqtSlot()
    def __selection_changed(self):
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
            bool(self.lstSettings.selectedItems())
        )

    @pyqtSlot()
    def __accepted(self):
        self.settings_to_add = [item.text() for item in self.lstSettings.selectedItems()]
