from qgis.PyQt.QtCore import pyqtSlot
from qgis.PyQt.QtWidgets import QDialog

from pg_service_parser.utils import get_ui_class

DIALOG_UI = get_ui_class("service_name_dialog.ui")


class ServiceNameDialog(QDialog, DIALOG_UI):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.buttonBox.accepted.connect(self.__accepted)
        self.service_name = "my-service"

    @pyqtSlot()
    def __accepted(self):
        if self.txtServiceName.text().strip():
            self.service_name = self.txtServiceName.text().replace(" ", "-")
