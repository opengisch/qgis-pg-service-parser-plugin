from qgis.core import QgsApplication
from qgis.gui import QgsMessageBar
from qgis.PyQt.QtCore import (
    QEvent,
    QItemSelection,
    QModelIndex,
    QObject,
    QPoint,
    QSortFilterProxyModel,
    Qt,
    pyqtSlot,
)
from qgis.PyQt.QtWidgets import (
    QAction,
    QApplication,
    QComboBox,
    QCompleter,
    QDialog,
    QHeaderView,
    QMenu,
    QMessageBox,
    QSizePolicy,
)

from pg_service_parser.conf.service_settings import SERVICE_SETTINGS, SETTINGS_TEMPLATE
from pg_service_parser.core.connection_model import ServiceConnectionModel
from pg_service_parser.core.copy_shortcuts import ShortcutsModel
from pg_service_parser.core.service_connections import (
    create_connection,
    edit_connection,
    get_connections,
    refresh_connections,
    remove_connection,
)
from pg_service_parser.core.setting_model import ServiceConfigModel
from pg_service_parser.gui.dlg_new_name import EnumNewName, NewNameDialog
from pg_service_parser.gui.dlg_service_settings import ServiceSettingsDialog
from pg_service_parser.gui.item_delegates import (
    ServiceConfigDelegate,
    ShortcutServiceDelegate,
)
from pg_service_parser.libs.pgserviceparser import (
    conf_path,
    copy_service_settings,
    create_service,
    remove_service,
    rename_service,
    service_config,
    service_names,
    write_service,
    write_service_to_text,
)
from pg_service_parser.utils import get_ui_class

DIALOG_UI = get_ui_class("pg_service_dialog.ui")
EDIT_TAB_INDEX = 0
SHORTCUTS_TAB_INDEX = 1
CONNECTION_TAB_INDEX = 2


class PgServiceDialog(QDialog, DIALOG_UI):
    def __init__(self, shortcuts_model: ShortcutsModel, iface):
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)

        self.iface = iface

        # Flag to handle initialization of new files
        self.__new_empty_file = False

        self.__shortcuts_model = shortcuts_model

        self.__conf_file_path = conf_path()
        self.__initialize_dialog()

    def __initialize_dialog(self):
        if not self.__conf_file_path.exists():
            self.btnCreateServiceFile.setIcon(QgsApplication.getThemeIcon("/mActionNewPage.svg"))
            self.btnCreateServiceFile.clicked.connect(self.__create_file_clicked)
            self.lblConfFile.setText(self.tr("Config file not found!"))
            not_found_tooltip = self.tr(
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

        # Edit tab icons
        self.btnAddService.setIcon(QgsApplication.getThemeIcon("/symbologyAdd.svg"))
        self.btnRemoveService.setIcon(QgsApplication.getThemeIcon("/symbologyRemove.svg"))
        self.btnAddSettings.setIcon(QgsApplication.getThemeIcon("/symbologyAdd.svg"))
        self.btnRemoveSetting.setIcon(QgsApplication.getThemeIcon("/symbologyRemove.svg"))
        self.btnCopySettings.setIcon(QgsApplication.getThemeIcon("/mActionEditCopy.svg"))
        # Connection tab icons
        self.btnAddConnection.setIcon(QgsApplication.getThemeIcon("/symbologyAdd.svg"))
        self.btnEditConnection.setIcon(QgsApplication.getThemeIcon("/symbologyEdit.svg"))
        self.btnRemoveConnection.setIcon(QgsApplication.getThemeIcon("/symbologyRemove.svg"))
        # Shortcuts tab icons
        self.shortcutAddButton.setIcon(QgsApplication.getThemeIcon("/symbologyAdd.svg"))
        self.shortcutRemoveButton.setIcon(QgsApplication.getThemeIcon("/symbologyRemove.svg"))
        self.txtConfFile.setText(str(self.__conf_file_path))
        self.lblWarning.setVisible(False)
        self.lblConfFile.setText(self.tr("Config file path found at "))
        self.lblConfFile.setToolTip("")
        self.txtConfFile.setVisible(True)
        self.tabWidget.setEnabled(True)
        self.btnCreateServiceFile.setVisible(False)
        self.tblServiceConnections.horizontalHeader().setVisible(True)
        self.btnRemoveSetting.setEnabled(False)
        self.btnRemoveService.setEnabled(False)
        self.shortcutRemoveButton.setEnabled(False)

        # Edit tab connections
        self.btnAddService.clicked.connect(self.__add_service_clicked)
        self.btnRemoveService.clicked.connect(self.__remove_service_clicked)
        self.lstServices.itemSelectionChanged.connect(self.__service_list_selection_changed)
        self.lstServices.customContextMenuRequested.connect(self.__service_list_context_menu)
        self.lstServices.itemDoubleClicked.connect(self.__service_list_double_clicked)
        self.tabWidget.currentChanged.connect(self.__current_tab_changed)
        self.btnAddSettings.clicked.connect(self.__add_settings_clicked)
        self.btnRemoveSetting.clicked.connect(self.__remove_setting_clicked)
        self.btnCopySettings.clicked.connect(self.__copy_settings_clicked)
        self.btnUpdateService.clicked.connect(self.__update_service_clicked)
        # Shortcuts tab connections
        self.shortcutAddButton.clicked.connect(self.__create_copy_shortcut)
        self.shortcutRemoveButton.clicked.connect(self.__remove_copy_shortcut)
        # Connection tab connections
        self.cboConnectionService.currentIndexChanged.connect(self.__connection_service_changed)
        self.btnAddConnection.clicked.connect(self.__add_connection_clicked)
        self.btnEditConnection.clicked.connect(self.__edit_connection_clicked)
        self.btnRemoveConnection.clicked.connect(self.__remove_connection_clicked)
        self.tblServiceConnections.doubleClicked.connect(self.__edit_double_clicked_connection)

        self.__make_combo_box_searchable(self.cboConnectionService)

        # Give all extra horizontal space to the editor panel, not the service list
        self.editTabHLayout.setStretch(0, 0)
        self.editTabHLayout.setStretch(1, 1)

        self.__initialize_edit_services()
        self.__initialize_shortcuts()
        self.__initialize_connection_services()
        self.__update_add_settings_button()
        self.__set_edit_panel_enabled(False)

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
                create_service(dlg.new_name, {})
            except PermissionError:
                self.permissionWarning()
            else:
                # Set flag to get a template after some initialization
                self.__new_empty_file = True
                self.__initialize_dialog()

    def __update_add_settings_button(self):
        # Make sure to call this method whenever the settings are added/removed
        enable = bool(self.__edit_model and self.__edit_model.rowCount() < len(SERVICE_SETTINGS()))
        self.btnAddSettings.setEnabled(enable)

    # ---- Edit Service Tab ----

    def __initialize_edit_services(self):
        self.__edit_model = None
        self.lstServices.blockSignals(True)
        selected_text = (
            self.lstServices.currentItem().text() if self.lstServices.currentItem() else ""
        )
        self.lstServices.clear()
        names = service_names(self.__conf_file_path, sorted_alphabetically=True)
        self.lstServices.addItems(names)
        self.lstServices.blockSignals(False)

        # Restore selection
        if selected_text:
            items = self.lstServices.findItems(selected_text, Qt.MatchFlag.MatchExactly)
            if items:
                self.lstServices.setCurrentItem(items[0])

    def __set_edit_panel_enabled(self, enabled):
        """Enable or disable the right-side settings editor panel."""
        self.editRightPanel.setEnabled(enabled)

    @pyqtSlot()
    def __service_list_selection_changed(self):
        selected_items = self.lstServices.selectedItems()
        count = len(selected_items)

        self.btnRemoveService.setEnabled(count > 0)

        if count == 1:
            # Single selection: load into editor
            self.__edit_service_selected(selected_items[0].text())
            self.__set_edit_panel_enabled(True)
        else:
            # Multi-selection or no selection: disable editor
            self.__edit_model = None
            self.tblServiceConfig.setModel(None)
            self.__set_edit_panel_enabled(False)
            self.btnUpdateService.setDisabled(True)
            self.__update_add_settings_button()

    def __edit_service_selected(self, service_name):
        """Load a service into the settings editor."""
        if self.__edit_model and self.__edit_model.is_dirty():
            if (
                QMessageBox.question(
                    self,
                    self.tr("Pending edits"),
                    self.tr(
                        "There are pending edits for service '{}'. Are you sure you want to discard them?"
                    ).format(self.__edit_model.service_name()),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                != QMessageBox.StandardButton.Yes
            ):
                # Restore previous selection
                self.lstServices.blockSignals(True)
                items = self.lstServices.findItems(
                    self.__edit_model.service_name(), Qt.MatchFlag.MatchExactly
                )
                if items:
                    self.lstServices.setCurrentItem(items[0])
                self.lstServices.blockSignals(False)
                return

        self.__edit_model = ServiceConfigModel(
            service_name, service_config(service_name, self.__conf_file_path)
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

    @pyqtSlot()
    def __add_service_clicked(self):
        dlg = NewNameDialog(EnumNewName.SERVICE, self)
        dlg.exec()
        if dlg.result() == QDialog.DialogCode.Accepted:
            try:
                create_service(dlg.new_name, {}, self.__conf_file_path)
            except PermissionError:
                self.permissionWarning()
            else:
                self.bar.pushSuccess(
                    self.tr("PG service"),
                    self.tr("Service '{}' created!").format(dlg.new_name),
                )
                self.__initialize_edit_services()
                # Select newly created service
                items = self.lstServices.findItems(dlg.new_name, Qt.MatchFlag.MatchExactly)
                if items:
                    self.lstServices.setCurrentItem(items[0])

    @pyqtSlot()
    def __remove_service_clicked(self):
        selected_items = self.lstServices.selectedItems()
        if not selected_items:
            return

        names = [item.text() for item in selected_items]
        if len(names) == 1:
            message = self.tr("Are you sure you want to remove the service '{}'?").format(names[0])
        else:
            message = self.tr("Are you sure you want to remove {} services?\n\n{}").format(
                len(names), "\n".join(names)
            )

        if (
            QMessageBox.question(
                self,
                self.tr("Remove service(s)"),
                message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        ):
            for name in names:
                try:
                    remove_service(name, self.__conf_file_path)
                except PermissionError:
                    self.permissionWarning()
                    return

            self.bar.pushSuccess(
                self.tr("PG service"),
                self.tr("{} service(s) removed.").format(len(names)),
            )
            self.__edit_model = None
            self.tblServiceConfig.setModel(None)
            self.__set_edit_panel_enabled(False)
            self.__initialize_edit_services()

    @pyqtSlot(QPoint)
    def __service_list_context_menu(self, pos):
        item = self.lstServices.itemAt(pos)
        if not item:
            return

        selected_items = self.lstServices.selectedItems()
        if len(selected_items) != 1:
            return

        menu = QMenu(self)
        rename_action = QAction(
            QgsApplication.getThemeIcon("/mActionRename.svg"),
            self.tr("Rename service..."),
            self,
        )
        rename_action.triggered.connect(lambda: self.__rename_service(item.text()))
        menu.addAction(rename_action)

        duplicate_action = QAction(
            QgsApplication.getThemeIcon("/mActionDuplicateLayer.svg"),
            self.tr("Duplicate service..."),
            self,
        )
        duplicate_action.triggered.connect(lambda: self.__duplicate_and_edit_service(item.text()))
        menu.addAction(duplicate_action)
        menu.exec(self.lstServices.viewport().mapToGlobal(pos))

    def __service_list_double_clicked(self, item):
        """Rename service on double-click."""
        if item:
            self.__rename_service(item.text())

    def __rename_service(self, old_name):
        """Rename a service."""
        dlg = NewNameDialog(EnumNewName.SERVICE, self)
        dlg.setWindowTitle(self.tr("Rename service"))
        dlg.label.setText(self.tr("Enter the new name for '{}'").format(old_name))
        dlg.txtNewName.setText(old_name)
        dlg.exec()
        if dlg.result() == QDialog.DialogCode.Accepted:
            new_name = dlg.new_name
            if new_name == old_name:
                return
            try:
                rename_service(old_name, new_name, self.__conf_file_path)
            except PermissionError:
                self.permissionWarning()
            else:
                self.bar.pushSuccess(
                    self.tr("PG service"),
                    self.tr("Service '{}' renamed to '{}'!").format(old_name, new_name),
                )
                self.__initialize_edit_services()
                items = self.lstServices.findItems(new_name, Qt.MatchFlag.MatchExactly)
                if items:
                    self.lstServices.setCurrentItem(items[0])

    def __duplicate_and_edit_service(self, source_service_name):
        """Duplicate a service with a new name and select it for editing."""
        dlg = NewNameDialog(EnumNewName.SERVICE, self)
        dlg.exec()
        if dlg.result() == QDialog.DialogCode.Accepted:
            target_name = dlg.new_name
            try:
                copy_service_settings(source_service_name, target_name, self.__conf_file_path)
            except PermissionError:
                self.permissionWarning()
            else:
                self.bar.pushSuccess(
                    self.tr("PG service"),
                    self.tr("Service '{}' duplicated to '{}'!").format(
                        source_service_name, target_name
                    ),
                )
                self.__initialize_edit_services()
                # Select duplicated service
                items = self.lstServices.findItems(target_name, Qt.MatchFlag.MatchExactly)
                if items:
                    self.lstServices.setCurrentItem(items[0])

    @pyqtSlot(QItemSelection, QItemSelection)
    def __update_settings_buttons(self, selected, deselected):
        self.btnRemoveSetting.setEnabled(bool(selected.indexes()))

    @pyqtSlot()
    def __add_settings_clicked(self):
        dlg = ServiceSettingsDialog(self, self.__edit_model.current_setting_keys())
        dlg.exec()

        if dlg.settings_to_add:
            settings = {
                k: v["default"] for k, v in SERVICE_SETTINGS().items() if k in dlg.settings_to_add
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
                    self.tr("Remove service setting"),
                    self.tr("Are you sure you want to remove the '{}' setting?").format(
                        setting_key
                    ),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                == QMessageBox.StandardButton.Yes
            ):
                self.__edit_model.remove_setting(selected_indexes[0])
                self.__update_add_settings_button()  # Settings removed

    @pyqtSlot()
    def __copy_settings_clicked(self):
        selected_items = self.lstServices.selectedItems()
        if not selected_items or len(selected_items) != 1:
            return

        service_name = selected_items[0].text()
        settings_text = write_service_to_text(service_name, self.__edit_model.service_config())
        QApplication.clipboard().setText(settings_text)
        self.bar.pushSuccess(
            "PG service", f"PG service '{service_name}' settings copied to clipboard!"
        )

    @pyqtSlot()
    def __update_service_clicked(self):
        if self.__edit_model and self.__edit_model.is_dirty():
            invalid = self.__edit_model.invalid_settings()
            if invalid:
                self.bar.pushWarning(
                    self.tr("PG service"),
                    self.tr(
                        "Settings '{}' have invalid values. Adjust them and try again."
                    ).format("', '".join(invalid)),
                )
                return

            selected_items = self.lstServices.selectedItems()
            if not selected_items or len(selected_items) != 1:
                return

            target_service = selected_items[0].text()
            try:
                write_service(
                    target_service, self.__edit_model.service_config(), self.__conf_file_path
                )
            except PermissionError:
                self.permissionWarning()
            else:
                self.bar.pushSuccess(
                    self.tr("PG service"),
                    self.tr("PG service '{}' updated!").format(target_service),
                )
                self.__edit_model.set_not_dirty()
        else:
            self.bar.pushInfo(
                self.tr("PG service"), self.tr("Edit the service configuration and try again.")
            )

    # ---- Shortcuts Tab ----

    def __initialize_shortcuts(self):
        self.shortcutsTableView.setModel(self.__shortcuts_model)
        self.__shortcut_delegate = ShortcutServiceDelegate(
            lambda: service_names(self.__conf_file_path, sorted_alphabetically=True),
            self,
        )
        self.shortcutsTableView.setItemDelegate(self.__shortcut_delegate)
        self.shortcutsTableView.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Interactive
        )
        self.shortcutsTableView.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Interactive
        )
        self.shortcutsTableView.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.shortcutsTableView.selectionModel().selectionChanged.connect(
            self.__shortcuts_selection_changed
        )
        self.shortcutsTableView.resizeColumnsToContents()

    @pyqtSlot()
    def __create_copy_shortcut(self):
        row = self.__shortcuts_model.add_empty_shortcut()
        self.shortcutsTableView.resizeColumnsToContents()
        # Select and start editing the new row (From column)
        index = self.__shortcuts_model.index(row, 1)
        self.shortcutsTableView.scrollTo(index)
        self.shortcutsTableView.edit(index)

    @pyqtSlot()
    def __remove_copy_shortcut(self):
        selectedIndexes = self.shortcutsTableView.selectedIndexes()
        if len(selectedIndexes) == 0:
            return

        shortcut = self.__shortcuts_model.data(selectedIndexes[0])

        res = QMessageBox.question(
            self,
            self.tr("Remove shortcut"),
            self.tr("Are you sure you want to remove the shortcut '{}'?").format(shortcut),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if res == QMessageBox.StandardButton.Yes:
            self.__shortcuts_model.remove_shortcut(selectedIndexes[0])

    @pyqtSlot(QItemSelection, QItemSelection)
    def __shortcuts_selection_changed(self, selected, deselected):
        self.shortcutRemoveButton.setEnabled(len(selected) > 0)

    # ---- Tab Changed ----

    @pyqtSlot(int)
    def __current_tab_changed(self, index):
        if index == SHORTCUTS_TAB_INDEX:
            pass  # Shortcuts are always up-to-date
        elif index == EDIT_TAB_INDEX:
            self.__initialize_edit_services()
        elif index == CONNECTION_TAB_INDEX:
            self.__initialize_connection_services()

    # ---- Connection Tab ----

    def __initialize_connection_services(self):
        self.__connection_model = None
        current_text = self.cboConnectionService.currentText()
        self.cboConnectionService.blockSignals(True)
        self.cboConnectionService.clear()
        self.cboConnectionService.blockSignals(False)
        self.cboConnectionService.addItems(
            [""] + service_names(self.__conf_file_path, sorted_alphabetically=True)
        )
        if current_text:
            self.cboConnectionService.setCurrentIndex(
                self.cboConnectionService.findText(current_text)
            )

    @pyqtSlot(int)
    def __connection_service_changed(self, index):
        self.__initialize_service_connections()

    def __initialize_service_connections(self, selected_index=QModelIndex()):
        service = self.cboConnectionService.currentText()
        self.__connection_model = ServiceConnectionModel(service, get_connections(service))
        self.__update_connection_controls(False)
        self.tblServiceConnections.setModel(self.__connection_model)
        self.tblServiceConnections.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
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
            self.__refresh_qgis_connections()

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
        self.__refresh_qgis_connections()

    @pyqtSlot()
    def __remove_connection_clicked(self):
        selected_indexes = self.tblServiceConnections.selectedIndexes()
        if selected_indexes:
            connection_name = self.__connection_model.index_to_connection_key(selected_indexes[0])
            if (
                QMessageBox.question(
                    self,
                    self.tr("Remove service connection"),
                    self.tr("Are you sure you want to remove the connection to '{}'?").format(
                        connection_name
                    ),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                == QMessageBox.StandardButton.Yes
            ):
                remove_connection(connection_name)
                self.__initialize_service_connections()
                self.__refresh_qgis_connections()

    @pyqtSlot(QItemSelection, QItemSelection)
    def __conn_table_selection_changed(self, selected, deselected):
        selected_indexes = bool(self.tblServiceConnections.selectedIndexes())
        self.__update_connection_controls(selected_indexes)

    def __update_connection_controls(self, enable):
        self.btnEditConnection.setEnabled(enable)
        self.btnRemoveConnection.setEnabled(enable)

    def __refresh_qgis_connections(self):
        refresh_connections(self.iface)

    def __make_combo_box_searchable(self, combo_box, allow_custom_name=False):
        """
        :param combo_box: Combo box object
        :param allow_custom_name: If False, the combo box should only display
                                  existing names when it has no focus
        """
        # Borrowed from https://gist.github.com/rBrenick/cb4c29f8a2d094e9df3e321a87eceb04
        combo_box.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        combo_box.setEditable(True)
        combo_box.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        filter_model = QSortFilterProxyModel(combo_box)
        filter_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        filter_model.setSourceModel(combo_box.model())

        completer = QCompleter(filter_model, combo_box)
        completer.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
        combo_box.setCompleter(completer)
        combo_box.lineEdit().textEdited.connect(filter_model.setFilterFixedString)

        if not allow_custom_name:
            combo_box.installEventFilter(ServiceComboBoxLostFocusFilter(combo_box, self))


class ServiceComboBoxLostFocusFilter(QObject):
    def __init__(self, combo_box, parent):
        super().__init__(parent)
        self.__combo_box = combo_box

    def eventFilter(self, object, event) -> bool:
        if event.type() == QEvent.Type.FocusOut:
            if object == self.__combo_box:
                # If a service combo box lost focus, we make sure
                # the text displayed corresponds to the currently
                # selected service (and not to the current edited text).
                self.reset_service()
        return False

    def reset_service(self):
        if self.__combo_box.currentText() != self.__combo_box.itemText(
            self.__combo_box.currentIndex()
        ):
            self.__combo_box.blockSignals(True)  # Avoid triggering custom slot while resetting
            self.__combo_box.setCurrentIndex(self.__combo_box.currentIndex())
            self.__combo_box.blockSignals(False)
