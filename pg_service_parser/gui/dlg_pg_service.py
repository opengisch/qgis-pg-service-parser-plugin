from qgis.gui import QgsMessageBar
from qgis.PyQt.QtCore import Qt, pyqtSlot
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QSizePolicy

from pg_service_parser.core.item_models import ServiceConfigModel
from pg_service_parser.core.pg_service_parser_wrapper import (
    conf_path,
    copy_service_settings,
    service_config,
    service_names,
    write_service,
)
from pg_service_parser.utils import get_ui_class

DIALOG_UI = get_ui_class("pg_service_dialog.ui")
COPY_TAB_INDEX = 0
EDIT_TAB_INDEX = 1


class PgServiceDialog(QDialog, DIALOG_UI):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        conf_file_path = conf_path()
        if not conf_file_path:
            self.lblConfFile.setText("Config file not found!")
            self.lblConfFile.setToolTip(
                "Set your PGSERVICEFILE environment variable and reopen the dialog."
            )
            self.txtConfFile.setVisible(False)
            self.tabWidget.setEnabled(False)
            return

        self.__edit_model = None

        self.txtConfFile.setText(str(conf_file_path))
        self.lblWarning.setVisible(False)

        self.radOverwrite.toggled.connect(self.__update_target_controls)
        self.btnCopyService.clicked.connect(self.__copy_service)
        self.cboSourceService.currentIndexChanged.connect(self.__source_service_changed)
        self.tabWidget.currentChanged.connect(self.__current_tab_changed)
        self.cboEditService.currentIndexChanged.connect(self.__edit_service_changed)
        self.btnUpdateService.clicked.connect(self.__update_service_clicked)

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

    def __initialize_edit_services(self):
        self.__edit_model = None
        current_text = self.cboEditService.currentText()  # Remember latest currentText
        self.cboEditService.blockSignals(True)  # Avoid triggering custom slot while clearing
        self.cboEditService.clear()
        self.cboEditService.blockSignals(False)
        self.cboEditService.addItems(service_names())
        self.cboEditService.setCurrentText(current_text)

    @pyqtSlot()
    def __copy_service(self):
        # Validations
        if self.radCreate.isChecked():
            if not self.txtNewService.text().strip():
                self.bar.pushInfo("PG service", "Enter a service name and try again.")
                return
            elif self.txtNewService.text().strip() in service_names():
                self.bar.pushWarning(
                    "PG service",
                    "Service name '{}' already exists! Change it and try again.".format(
                        self.txtNewService.text().strip()
                    ),
                )
                return
        elif self.radOverwrite.isChecked():
            if not self.cboTargetService.currentText():
                self.bar.pushInfo("PG service", "Select a valid target service and try again.")
                return

        target_service = (
            self.cboTargetService.currentText()
            if self.radOverwrite.isChecked()
            else self.txtNewService.text().strip()
        )

        copy_service_settings(self.cboSourceService.currentText(), target_service)
        self.bar.pushSuccess("PG service", f"PG service copied to '{target_service}'!")
        if self.radCreate.isChecked():
            self.__initialize_copy_services()  # Reflect the newly added service

    @pyqtSlot(int)
    def __current_tab_changed(self, index):
        if index == COPY_TAB_INDEX:
            # self.__initialize_copy_services()
            pass  # For now, services to be copied won't be altered in other tabs
        elif index == EDIT_TAB_INDEX:
            self.__initialize_edit_services()

    @pyqtSlot(int)
    def __edit_service_changed(self, index):
        target_service = self.cboEditService.currentText()
        if self.__edit_model and self.__edit_model.is_dirty():
            if (
                not QMessageBox.question(
                    self,
                    "Pending edits",
                    "There are pending edits for service '{}'. Are you sure you want to discard them?".format(
                        self.__edit_model.service_name()
                    ),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                == QMessageBox.Yes
            ):

                self.cboEditService.blockSignals(True)
                self.cboEditService.setCurrentText(self.__edit_model.service_name())
                self.cboEditService.blockSignals(False)
                return

        self.__edit_model = ServiceConfigModel(target_service, service_config(target_service))
        self.tblServiceConfig.setModel(self.__edit_model)

    @pyqtSlot()
    def __update_service_clicked(self):
        if self.__edit_model and self.__edit_model.is_dirty():
            target_service = self.cboEditService.currentText()
            write_service(target_service, self.__edit_model.service_config())
            self.bar.pushSuccess("PG service", f"PG service '{target_service}' updated!")
            self.__edit_model.set_not_dirty()
        else:
            self.bar.pushInfo("PG service", "Edit the service configuration and try again.")
