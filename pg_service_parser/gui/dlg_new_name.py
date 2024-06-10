from enum import Enum

from qgis.PyQt.QtCore import pyqtSlot
from qgis.PyQt.QtWidgets import QDialog, QWidget

from pg_service_parser.utils import get_ui_class

DIALOG_UI = get_ui_class("new_name_dialog.ui")


class EnumNewName(Enum):
    SERVICE = 0
    CONNECTION = 1


class NewNameDialog(QDialog, DIALOG_UI):

    def __init__(self, mode: EnumNewName, parent: QWidget, data: str = "") -> None:
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.__mode = mode

        self.buttonBox.accepted.connect(self.__accepted)

        if self.__mode == EnumNewName.SERVICE:
            self.setWindowTitle("Service name")
            self.label.setText("Enter a service name")
            self.txtNewName.setPlaceholderText("e.g., my-service")
            self.new_name = "my-service"
        elif self.__mode == EnumNewName.CONNECTION:
            self.setWindowTitle("Connection name")
            self.label.setText("Enter a connection name")
            self.txtNewName.setPlaceholderText("e.g., My Service Connection")
            self.new_name = f"{data} connection"

    @pyqtSlot()
    def __accepted(self):
        if self.txtNewName.text().strip():
            if self.__mode == EnumNewName.SERVICE:
                self.new_name = self.txtNewName.text().strip().replace(" ", "-")
            elif self.__mode == EnumNewName.CONNECTION:
                self.new_name = self.txtNewName.text().strip()
