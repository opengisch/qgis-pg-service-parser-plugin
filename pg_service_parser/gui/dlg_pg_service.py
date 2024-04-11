from qgis.PyQt.QtCore import (Qt,
                              pyqtSlot)
from qgis.PyQt.QtWidgets import (QDialog,
                                 QSizePolicy)
from qgis.gui import QgsMessageBar

from pg_service_parser.pg_service_parser_wrapper import (conf_path,
                                                         copy_service_settings,
                                                         service_names)
from pg_service_parser.utils import get_ui_class

DIALOG_UI = get_ui_class('pg_service_dialog.ui')
COPY_TAB_INDEX = 0
EDIT_TAB_INDEX = 1


class PgServiceDialog(QDialog, DIALOG_UI):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        conf_file_path = conf_path()
        if not conf_file_path:
            self.lblConfFile.setText("Config file not found!")
            self.lblConfFile.setToolTip("Set your PGSERVICEFILE environment variable and reopen the dialog.")
            self.txtConfFile.setVisible(False)
            self.tabWidget.setEnabled(False)
            return

        self.txtConfFile.setText(conf_file_path)
        self.lblWarning.setVisible(False)
        self.tabWidget.setTabEnabled(EDIT_TAB_INDEX, False)  # Not yet implemented

        self.radOverwrite.toggled.connect(self.__update_target_controls)
        self.btnCopyService.clicked.connect(self.__copy_service)
        self.cboSourceService.currentIndexChanged.connect(self.__source_service_changed)

        self.__initialize_copy_services()
        self.__update_target_controls(True)

        self.bar = QgsMessageBar()
        self.bar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout().insertWidget(0, self.bar)

    @pyqtSlot(bool)
    def __update_target_controls(self, checked):
        self.cboTargetService.setEnabled(self.radOverwrite.isChecked())
        self.txtNewService.setEnabled(not self.radOverwrite.isChecked())

    @pyqtSlot(int)
    def __source_service_changed(self, index):
        # Remember latest currentText only if current item in source
        # is different from current item in target
        current_text = self.cboTargetService.currentText()
        current_text = current_text if self.cboSourceService.currentText() != current_text else ""

        self.cboTargetService.clear()
        self.cboTargetService.addItems([""] + service_names())

        model = self.cboTargetService.model()
        item = model.item(index + 1)  # Account for the first (empty) item
        item.setFlags(item.flags() & ~Qt.ItemIsEnabled)  # Disable mirror item

        self.cboTargetService.setCurrentText(current_text)

    def __initialize_copy_services(self):
        current_text = self.cboSourceService.currentText()  # Remember latest currentText
        self.cboSourceService.blockSignals(True)  # Avoid triggering custom slot while clearing
        self.cboSourceService.clear()
        self.cboSourceService.blockSignals(False)
        self.cboSourceService.addItems(service_names())
        self.cboSourceService.setCurrentText(current_text)

    def __copy_service(self):
        # Validations
        if self.radCreate.isChecked():
            if not self.txtNewService.text().strip():
                self.bar.pushInfo("PG service", "Enter a service name and try again.")
                return
            elif self.txtNewService.text().strip() in service_names():
                self.bar.pushWarning("PG service", "Service name already exists! Change it and try again.")
                return
        elif self.radOverwrite.isChecked():
            if not self.cboTargetService.currentText():
                self.bar.pushInfo("PG service", "Select a valid target service and try again.")
                return

        target_service = self.cboTargetService.currentText() if self.radOverwrite.isChecked() else self.txtNewService.text().strip()

        if copy_service_settings(self.cboSourceService.currentText(), target_service):
            self.bar.pushSuccess("PG service", f"PG service copied to '{target_service}'!")
            if self.radCreate.isChecked():
                self.__initialize_copy_services()  # Reflect the newly added service
        else:
            self.bar.pushWarning("PG service", "There was a problem copying the service!")
