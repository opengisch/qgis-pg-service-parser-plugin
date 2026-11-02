from pathlib import Path

from qgis.core import QgsApplication
from qgis.PyQt.QtCore import Qt, pyqtSlot
from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QTreeWidgetItem,
)

from pg_service_parser.core.service_tester import ServiceTesterTask, psycopg_available
from pg_service_parser.libs.pgserviceparser import (
    disabled_service_config,
    disabled_service_names,
    service_names,
)
from pg_service_parser.utils import get_ui_class

DIALOG_UI = get_ui_class("service_test_dialog.ui")


class ServiceRestoreDialog(QDialog, DIALOG_UI):
    """Lists the disabled services and tests them in the background.

    The services that can be connected are pre-checked. Once the dialog is accepted,
    services_to_restore holds the services to restore.
    """

    def __init__(self, parent, conf_file_path: Path):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr("Restore disabled services"))
        self.treeServices.setHeaderLabels([self.tr("Service"), self.tr("Status")])
        self.treeServices.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        self.services_to_restore = []
        self.__task = None
        self.__items = {}
        self.__succeeded_count = 0

        existing_names = service_names(conf_file_path)
        services_to_test = {}
        for name in sorted(disabled_service_names(conf_file_path), key=str.lower):
            item = QTreeWidgetItem([name])
            if name in existing_names:
                self.__flag(item, self.tr("A service with the same name already exists"))
                item.setDisabled(True)
            else:
                item.setCheckState(0, Qt.CheckState.Unchecked)
                self.__items[name] = item
                services_to_test[name] = disabled_service_config(name, conf_file_path)
            self.treeServices.addTopLevelItem(item)

        self.treeServices.itemChanged.connect(self.__update_restore_button)
        self.__restore_button = self.buttonBox.addButton(
            self.tr("Restore checked services"), QDialogButtonBox.ButtonRole.ActionRole
        )
        self.__restore_button.clicked.connect(self.__restore_clicked)
        self.__update_restore_button()

        if not services_to_test or not psycopg_available():
            self.progressBar.hide()
            for item in self.__items.values():
                item.setCheckState(0, Qt.CheckState.Checked)
            status = self.tr("Check the services to restore.")
            if services_to_test:
                status = self.tr(
                    "Testing services requires the psycopg or psycopg2 Python package. {}"
                ).format(status)
            self.lblStatus.setText(status)
            return

        for item in self.__items.values():
            item.setText(1, self.tr("Testing..."))
        self.lblStatus.setText(
            self.tr("Testing {} disabled service(s)...").format(len(services_to_test))
        )

        self.__task = ServiceTesterTask(services_to_test)
        self.__task.progressChanged.connect(
            lambda progress: self.progressBar.setValue(int(progress))
        )
        self.__task.service_tested.connect(self.__service_tested)
        self.__task.taskCompleted.connect(self.__test_completed)
        self.__task.taskTerminated.connect(self.__test_terminated)
        QgsApplication.taskManager().addTask(self.__task)

    def done(self, result):
        if self.__task:
            self.__task.cancel()
        super().done(result)

    def __flag(self, item: QTreeWidgetItem, error: str):
        item.setIcon(1, QgsApplication.getThemeIcon("/mIconWarning.svg"))
        item.setText(1, error.splitlines()[0])
        item.setToolTip(1, error)

    @pyqtSlot(str, str)
    def __service_tested(self, service_name, error):
        item = self.__items[service_name]
        if error:
            self.__flag(item, error)
        else:
            self.__succeeded_count += 1
            item.setIcon(1, QgsApplication.getThemeIcon("/mIconSuccess.svg"))
            item.setText(1, self.tr("Connection succeeded"))
            item.setCheckState(0, Qt.CheckState.Checked)

    @pyqtSlot()
    def __test_completed(self):
        self.__task = None
        self.progressBar.hide()
        self.lblStatus.setText(
            self.tr(
                "Connection succeeded for {} of {} disabled service(s). "
                "Check the services to restore."
            ).format(self.__succeeded_count, len(self.__items))
        )

    @pyqtSlot()
    def __test_terminated(self):
        self.__task = None
        self.progressBar.hide()
        self.lblStatus.setText(self.tr("The test was canceled. Check the services to restore."))

    def __checked_services(self) -> list[str]:
        return [
            name
            for name, item in self.__items.items()
            if item.checkState(0) == Qt.CheckState.Checked
        ]

    @pyqtSlot()
    def __update_restore_button(self):
        self.__restore_button.setEnabled(bool(self.__checked_services()))

    @pyqtSlot()
    def __restore_clicked(self):
        self.services_to_restore = self.__checked_services()
        self.accept()
