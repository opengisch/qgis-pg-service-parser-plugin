from qgis.PyQt.QtCore import pyqtSlot
from qgis.PyQt.QtWidgets import QDialog

from pg_service_parser.conf.service_settings import SERVICE_SETTINGS
from pg_service_parser.utils import get_ui_class

DIALOG_UI = get_ui_class("service_settings_dialog.ui")


class ServiceSettingsDialog(QDialog, DIALOG_UI):

    def __init__(self, parent, settings_to_hide: list[str]):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.buttonBox.accepted.connect(self.__accepted)

        settings = set(SERVICE_SETTINGS.keys()) - set(settings_to_hide)
        self.lstSettings.addItems(settings)
        self.settings_to_add = []

    @pyqtSlot()
    def __accepted(self):
        self.settings_to_add = [item.text() for item in self.lstSettings.selectedItems()]
