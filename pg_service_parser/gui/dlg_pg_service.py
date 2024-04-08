from qgis.PyQt.QtCore import pyqtSlot
from qgis.PyQt.QtWidgets import QDialog

from pg_service_parser.pg_service_parser_wrapper import (copy_service_settings,
                                                         service_names)
from pg_service_parser.utils import get_ui_class

DIALOG_UI = get_ui_class('pg_service_dialog.ui')


class PgServiceDialog(QDialog, DIALOG_UI):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.cboSourceService.addItems(service_names())
        self.cboTargetService.addItems(service_names())

        self.radOverwrite.toggled.connect(self.__update_target_controls)
        self.buttonBox.accepted.connect(self.__accepted)

        self.__update_target_controls(True)

    @pyqtSlot(bool)
    def __update_target_controls(self, checked):
        self.cboTargetService.setEnabled(self.radOverwrite.isChecked())
        self.txtNewService.setEnabled(not self.radOverwrite.isChecked())

    def __accepted(self):
        target_service = self.cboTargetService.currentText() if self.radOverwrite.isChecked() else self.txtNewService.text()

        res = copy_service_settings(self.cboSourceService.currentText(), target_service)
        print(res)
