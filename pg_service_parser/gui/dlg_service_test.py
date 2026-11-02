from qgis.core import QgsApplication
from qgis.PyQt.QtCore import Qt, pyqtSlot
from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QTreeWidgetItem,
)

from pg_service_parser.core.service_tester import ServiceTesterTask
from pg_service_parser.gui.remove_services import ask_remove_action
from pg_service_parser.utils import get_ui_class

DIALOG_UI = get_ui_class("service_test_dialog.ui")


class ServiceTestDialog(QDialog, DIALOG_UI):
    """Tests the services in the background and lists the failing ones.

    Once the dialog is accepted, services_to_remove holds the services to remove
    and remove_action how to remove them.
    """

    def __init__(self, parent, service_names: list[str]):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.services_to_remove = []
        self.remove_action = None
        self.__service_count = len(service_names)

        self.treeServices.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.treeServices.itemChanged.connect(self.__update_remove_button)
        self.__remove_button = self.buttonBox.addButton(
            self.tr("Remove checked services..."), QDialogButtonBox.ButtonRole.ActionRole
        )
        self.__remove_button.setEnabled(False)
        self.__remove_button.clicked.connect(self.__remove_clicked)

        self.lblStatus.setText(self.tr("Testing {} service(s)...").format(self.__service_count))

        self.__task = ServiceTesterTask({name: {"service": name} for name in service_names})
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

    @pyqtSlot(str, str)
    def __service_tested(self, service_name, error):
        if not error:
            return
        item = QTreeWidgetItem([service_name, error.splitlines()[0]])
        item.setCheckState(0, Qt.CheckState.Checked)
        item.setToolTip(1, error)
        self.treeServices.addTopLevelItem(item)

    @pyqtSlot()
    def __test_completed(self):
        self.__task = None
        self.progressBar.hide()
        failed_count = self.treeServices.topLevelItemCount()
        if failed_count:
            self.treeServices.sortItems(0, Qt.SortOrder.AscendingOrder)
            self.lblStatus.setText(
                self.tr(
                    "Connection failed for {} of {} service(s). "
                    "Check the services to remove from the service file."
                ).format(failed_count, self.__service_count)
            )
            self.__update_remove_button()
        else:
            self.treeServices.hide()
            self.__remove_button.hide()
            self.lblStatus.setText(
                self.tr("Connection succeeded for all {} service(s).").format(self.__service_count)
            )

    @pyqtSlot()
    def __test_terminated(self):
        self.__task = None
        self.progressBar.hide()
        self.lblStatus.setText(self.tr("The test was canceled."))

    def __checked_services(self) -> list[str]:
        items = [
            self.treeServices.topLevelItem(i) for i in range(self.treeServices.topLevelItemCount())
        ]
        return [item.text(0) for item in items if item.checkState(0) == Qt.CheckState.Checked]

    @pyqtSlot()
    def __update_remove_button(self):
        self.__remove_button.setEnabled(self.__task is None and bool(self.__checked_services()))

    @pyqtSlot()
    def __remove_clicked(self):
        names = self.__checked_services()
        if action := ask_remove_action(self, names):
            self.services_to_remove = names
            self.remove_action = action
            self.accept()
