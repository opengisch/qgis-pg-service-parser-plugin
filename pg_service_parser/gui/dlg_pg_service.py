from qgis.core import QgsApplication
from qgis.gui import QgsMessageBar
from qgis.PyQt.QtCore import QItemSelection, QModelIndex, Qt, pyqtSlot
from qgis.PyQt.QtWidgets import QDialog, QHeaderView, QMessageBox, QSizePolicy

from pg_service_parser.conf.service_settings import SERVICE_SETTINGS, SETTINGS_TEMPLATE
from pg_service_parser.core.connection_model import ServiceConnectionModel
from pg_service_parser.core.copy_shortcuts import ShortcutsModel
from pg_service_parser.core.pg_service_parser_wrapper import (
    add_new_service,
    conf_path,
    copy_service_settings,
    service_config,
    service_names,
    write_service,
)
from pg_service_parser.core.service_connections import (
    create_connection,
    edit_connection,
    get_connections,
    remove_connection,
)
from pg_service_parser.core.setting_model import ServiceConfigModel
from pg_service_parser.gui.dlg_new_name import EnumNewName, NewNameDialog
from pg_service_parser.gui.dlg_service_settings import ServiceSettingsDialog
from pg_service_parser.gui.item_delegates import ServiceConfigDelegate
from pg_service_parser.utils import get_ui_class

DIALOG_UI = get_ui_class("pg_service_dialog.ui")
EDIT_TAB_INDEX = 0
COPY_TAB_INDEX = 1
CONNECTION_TAB_INDEX = 2
PERMISSION_ERROR_MESSAGE = """
The PG service file is read-only and cannot be updated.

To fix this, make sure you have enough permissions and retry.
Otherwise, you can use PGSERVICEFILE or PGSYSCONFDIR environment
variables to point to a PG service file located in a folder
where you have write permission.
"""


class PgServiceDialog(QDialog, DIALOG_UI):
    def __init__(self, shortcuts_model: ShortcutsModel, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        # Flag to handle initialization of new files
        self.__new_empty_file = False

        self.__shortcuts_model = shortcuts_model

        self.__conf_file_path = conf_path()
        self.__initialize_dialog()

    def __initialize_dialog(self):
        if not self.__conf_file_path.exists():
            self.btnCreateServiceFile.setIcon(QgsApplication.getThemeIcon("/mActionNewPage.svg"))
            self.btnCreateServiceFile.clicked.connect(self.__create_file_clicked)
            self.lblConfFile.setText("Config file not found!")
            not_found_tooltip = (
                "Create a config file at a default location or\n"
                "set your PGSERVICEFILE environment variable and reopen the dialog."
            )
            self.lblConfFile.setToolTip(not_found_tooltip)
            self.lblWarning.setToolTip(not_found_tooltip)
            self.txtConfFile.setVisible(False)
            self.tabWidget.setEnabled(False)
            return

        self.__edit_model = None
        self.__connection_model = None

        self.btnAddSettings.setIcon(QgsApplication.getThemeIcon("/symbologyAdd.svg"))
        self.btnRemoveSetting.setIcon(QgsApplication.getThemeIcon("/symbologyRemove.svg"))
        self.btnAddConnection.setIcon(QgsApplication.getThemeIcon("/symbologyAdd.svg"))
        self.btnEditConnection.setIcon(QgsApplication.getThemeIcon("/symbologyEdit.svg"))
        self.btnRemoveConnection.setIcon(QgsApplication.getThemeIcon("/symbologyRemove.svg"))
        self.shortcutAddButton.setIcon(QgsApplication.getThemeIcon("/symbologyAdd.svg"))
        self.shortcutRemoveButton.setIcon(QgsApplication.getThemeIcon("/symbologyRemove.svg"))
        self.txtConfFile.setText(str(self.__conf_file_path))
        self.lblWarning.setVisible(False)
        self.lblConfFile.setText("Config file path found at ")
        self.lblConfFile.setToolTip("")
        self.txtConfFile.setVisible(True)
        self.tabWidget.setEnabled(True)
        self.btnCreateServiceFile.setVisible(False)
        self.tblServiceConnections.horizontalHeader().setVisible(True)
        self.btnRemoveSetting.setEnabled(False)
        self.shortcutRemoveButton.setEnabled(False)

        self.radOverwrite.toggled.connect(self.__update_target_controls)
        self.btnCopyService.clicked.connect(self.__copy_service)
        self.shortcutAddButton.clicked.connect(self.__create_copy_shortcut)
        self.shortcutRemoveButton.clicked.connect(self.__remove_copy_shortcut)
        self.cboSourceService.currentIndexChanged.connect(self.__source_service_changed)
        self.tabWidget.currentChanged.connect(self.__current_tab_changed)
        self.cboEditService.currentIndexChanged.connect(self.__edit_service_changed)
        self.btnAddSettings.clicked.connect(self.__add_settings_clicked)
        self.btnRemoveSetting.clicked.connect(self.__remove_setting_clicked)
        self.btnUpdateService.clicked.connect(self.__update_service_clicked)
        self.cboConnectionService.currentIndexChanged.connect(self.__connection_service_changed)
        self.btnAddConnection.clicked.connect(self.__add_connection_clicked)
        self.btnEditConnection.clicked.connect(self.__edit_connection_clicked)
        self.btnRemoveConnection.clicked.connect(self.__remove_connection_clicked)
        self.tblServiceConnections.doubleClicked.connect(self.__edit_double_clicked_connection)

        self.__initialize_edit_services()
        self.__initialize_copy_services()
        self.__initialize_connection_services()
        self.__update_target_controls(True)
        self.__update_add_settings_button()

        self.bar = QgsMessageBar()
        self.bar.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout().insertWidget(0, self.bar)

    @pyqtSlot()
    def __create_file_clicked(self):
        dlg = NewNameDialog(EnumNewName.SERVICE, self)
        dlg.exec()
        if dlg.result() == QDialog.DialogCode.Accepted:
            self.__conf_file_path = conf_path(create_if_missing=True)

            try:
                add_new_service(dlg.new_name)
            except PermissionError:
                self.bar.pushWarning("PG service", PERMISSION_ERROR_MESSAGE)
            else:
                # Set flag to get a template after some initialization
                self.__new_empty_file = True
                self.__initialize_dialog()

    @pyqtSlot(bool)
    def __update_target_controls(self, checked):
        self.cboTargetService.setEnabled(self.radOverwrite.isChecked())
        self.txtNewService.setEnabled(not self.radOverwrite.isChecked())
        self.shortcutAddButton.setEnabled(self.radOverwrite.isChecked())

    def __update_add_settings_button(self):
        # Make sure to call this method whenever the settings are added/removed
        enable = self.__edit_model and self.__edit_model.rowCount() < len(SERVICE_SETTINGS)
        self.btnAddSettings.setEnabled(enable)

    @pyqtSlot(int)
    def __source_service_changed(self, index):
        # Remember latest currentText only if current item in source
        # is different from current item in target
        current_text = self.cboTargetService.currentText()
        current_text = current_text if self.cboSourceService.currentText() != current_text else ""

        self.cboTargetService.clear()
        self.cboTargetService.addItems([""] + service_names(self.__conf_file_path))

        model = self.cboTargetService.model()
        item = model.item(index + 1)  # Account for the first (empty) item
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)  # Disable mirror item

        self.cboTargetService.setCurrentText(current_text)

    def __initialize_copy_services(self):
        current_text = self.cboSourceService.currentText()  # Remember latest currentText
        self.cboSourceService.blockSignals(True)  # Avoid triggering custom slot while clearing
        self.cboSourceService.clear()
        self.cboSourceService.blockSignals(False)
        self.cboSourceService.addItems(service_names(self.__conf_file_path))
        self.cboSourceService.setCurrentText(current_text)

        self.shortcutsTableView.setModel(self.__shortcuts_model)
        self.shortcutsTableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.shortcutsTableView.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.shortcutsTableView.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.shortcutsTableView.selectionModel().selectionChanged.connect(
            self.__shortcuts_selection_changed
        )
        self.shortcutsTableView.resizeColumnsToContents()

    def __initialize_edit_services(self):
        self.__edit_model = None
        current_text = self.cboEditService.currentText()  # Remember latest currentText
        self.cboEditService.blockSignals(True)  # Avoid triggering custom slot while clearing
        self.cboEditService.clear()
        self.cboEditService.blockSignals(False)
        self.cboEditService.addItems(service_names(self.__conf_file_path))
        self.cboEditService.setCurrentText(current_text)

    def __initialize_connection_services(self):
        self.__connection_model = None
        current_text = self.cboConnectionService.currentText()  # Remember latest currentText
        self.cboConnectionService.blockSignals(True)  # Avoid triggering custom slot while clearing
        self.cboConnectionService.clear()
        self.cboConnectionService.blockSignals(False)
        self.cboConnectionService.addItems(service_names(self.__conf_file_path))
        self.cboConnectionService.setCurrentText(current_text)

    @pyqtSlot()
    def __copy_service(self):
        # Validations
        if self.radCreate.isChecked():
            if not self.txtNewService.text().strip():
                self.bar.pushInfo("PG service", "Enter a service name and try again.")
                return
            elif self.txtNewService.text().strip() in service_names(self.__conf_file_path):
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

        try:
            copy_service_settings(
                self.cboSourceService.currentText(), target_service, self.__conf_file_path
            )
        except PermissionError:
            self.bar.pushWarning("PG service", PERMISSION_ERROR_MESSAGE)
        else:
            self.bar.pushSuccess("PG service", f"PG service copied to '{target_service}'!")
            if self.radCreate.isChecked():
                self.__initialize_copy_services()  # Reflect the newly added service

    @pyqtSlot()
    def __create_copy_shortcut(self):
        target_service = self.cboTargetService.currentText()

        if not target_service:
            self.bar.pushInfo("PG service", "Select a valid target service and try again.")
            return
        self.__shortcuts_model.add_shortcut(self.cboSourceService.currentText(), target_service)
        self.shortcutsTableView.resizeColumnsToContents()

    @pyqtSlot()
    def __remove_copy_shortcut(self):
        selectedIndexes = self.shortcutsTableView.selectedIndexes()
        if len(selectedIndexes) == 0:
            return

        shortcut = self.__shortcuts_model.data(selectedIndexes[0])

        res = QMessageBox.question(
            self,
            "Remove shortcut",
            f"Are you sure you want to remove the shortcut '{shortcut}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if res == QMessageBox.StandardButton.Yes:
            self.__shortcuts_model.remove_shortcut(selectedIndexes[0])

    @pyqtSlot(int)
    def __current_tab_changed(self, index):
        if index == COPY_TAB_INDEX:
            # self.__initialize_copy_services()
            pass  # For now, services to be copied won't be altered in other tabs
        elif index == EDIT_TAB_INDEX:
            self.__initialize_edit_services()
        elif index == CONNECTION_TAB_INDEX:
            self.__initialize_connection_services()

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
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                == QMessageBox.StandardButton.Yes
            ):

                self.cboEditService.blockSignals(True)
                self.cboEditService.setCurrentText(self.__edit_model.service_name())
                self.cboEditService.blockSignals(False)
                return

        self.__edit_model = ServiceConfigModel(
            target_service, service_config(target_service, self.__conf_file_path)
        )
        self.tblServiceConfig.setModel(self.__edit_model)
        self.tblServiceConfig.setItemDelegate(ServiceConfigDelegate(self))
        self.tblServiceConfig.selectionModel().selectionChanged.connect(
            self.__update_settings_buttons
        )
        self.__edit_model.is_dirty_changed.connect(self.btnUpdateService.setEnabled)
        self.btnUpdateService.setDisabled(True)

        if self.__new_empty_file:
            # Add service template
            self.__edit_model.add_settings(SETTINGS_TEMPLATE)
            self.__new_empty_file = False

        self.__update_add_settings_button()  # Model just created
        self.__update_settings_buttons(QItemSelection(), QItemSelection())

    @pyqtSlot(QItemSelection, QItemSelection)
    def __update_settings_buttons(self, selected, deselected):
        self.btnRemoveSetting.setEnabled(bool(selected.indexes()))

    @pyqtSlot()
    def __add_settings_clicked(self):
        dlg = ServiceSettingsDialog(self, self.__edit_model.current_setting_keys())
        dlg.exec()

        if dlg.settings_to_add:
            settings = {
                k: v["default"] for k, v in SERVICE_SETTINGS.items() if k in dlg.settings_to_add
            }
            self.__edit_model.add_settings(settings)
            self.__update_add_settings_button()  # Settings added

    @pyqtSlot()
    def __remove_setting_clicked(self):
        selected_indexes = self.tblServiceConfig.selectedIndexes()
        if selected_indexes:
            setting_key = self.__edit_model.index_to_setting_key(selected_indexes[0])
            if (
                QMessageBox.question(
                    self,
                    "Remove service setting",
                    f"Are you sure you want to remove the '{setting_key}' setting?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                == QMessageBox.StandardButton.Yes
            ):
                self.__edit_model.remove_setting(selected_indexes[0])
                self.__update_add_settings_button()  # Settings removed

    @pyqtSlot()
    def __update_service_clicked(self):
        if self.__edit_model and self.__edit_model.is_dirty():
            invalid = self.__edit_model.invalid_settings()
            if invalid:
                self.bar.pushWarning(
                    "PG service",
                    "Settings '{}' have invalid values. Adjust them and try again.".format(
                        "', '".join(invalid)
                    ),
                )
                return

            target_service = self.cboEditService.currentText()
            try:
                write_service(
                    target_service, self.__edit_model.service_config(), self.__conf_file_path
                )
            except PermissionError:
                self.bar.pushWarning("PG service", PERMISSION_ERROR_MESSAGE)
            else:
                self.bar.pushSuccess("PG service", f"PG service '{target_service}' updated!")
                self.__edit_model.set_not_dirty()
        else:
            self.bar.pushInfo("PG service", "Edit the service configuration and try again.")

    @pyqtSlot(int)
    def __connection_service_changed(self, index):
        self.__initialize_service_connections()

    def __initialize_service_connections(self, selected_index=QModelIndex()):
        service = self.cboConnectionService.currentText()
        self.__connection_model = ServiceConnectionModel(service, get_connections(service))
        self.__update_connection_controls(False)
        self.tblServiceConnections.setModel(self.__connection_model)
        self.tblServiceConnections.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )

        self.tblServiceConnections.selectionModel().selectionChanged.connect(
            self.__conn_table_selection_changed
        )
        self.tblServiceConnections.selectRow(selected_index.row())  # Remember selection

    @pyqtSlot()
    def __add_connection_clicked(self):
        service = self.cboConnectionService.currentText()
        dlg = NewNameDialog(EnumNewName.CONNECTION, self, service)
        dlg.exec()
        if dlg.result() == QDialog.DialogCode.Accepted:
            create_connection(service, dlg.new_name)
            self.__initialize_service_connections()

    @pyqtSlot()
    def __edit_connection_clicked(self):
        selected_indexes = self.tblServiceConnections.selectedIndexes()
        if selected_indexes:
            self.__edit_connection(selected_indexes[0])

    @pyqtSlot(QModelIndex)
    def __edit_double_clicked_connection(self, index):
        self.__edit_connection(index)

    def __edit_connection(self, index):
        connection_name = self.__connection_model.index_to_connection_key(index)
        edit_connection(connection_name, self)
        self.__initialize_service_connections(index)

    @pyqtSlot()
    def __remove_connection_clicked(self):
        selected_indexes = self.tblServiceConnections.selectedIndexes()
        if selected_indexes:
            connection_name = self.__connection_model.index_to_connection_key(selected_indexes[0])
            if (
                QMessageBox.question(
                    self,
                    "Remove service connection",
                    f"Are you sure you want to remove the connection to '{connection_name}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                == QMessageBox.StandardButton.Yes
            ):
                remove_connection(connection_name)
                self.__initialize_service_connections()

    @pyqtSlot(QItemSelection, QItemSelection)
    def __conn_table_selection_changed(self, selected, deselected):
        selected_indexes = bool(self.tblServiceConnections.selectedIndexes())
        self.__update_connection_controls(selected_indexes)

    def __update_connection_controls(self, enable):
        self.btnEditConnection.setEnabled(enable)
        self.btnRemoveConnection.setEnabled(enable)

    @pyqtSlot(QItemSelection, QItemSelection)
    def __shortcuts_selection_changed(self, selected, deselected):
        self.shortcutRemoveButton.setEnabled(len(selected) > 0)
