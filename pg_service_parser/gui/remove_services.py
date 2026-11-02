from enum import Enum

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QMessageBox, QWidget


class RemoveAction(Enum):
    DELETE = "delete"
    DISABLE = "disable"


def tr(text: str) -> str:
    return QCoreApplication.translate("RemoveServices", text)


def ask_remove_action(parent: QWidget, service_names: list[str]) -> RemoveAction | None:
    """Asks whether to delete the services or to disable them (comment out).

    Returns None if canceled.
    """
    message_box = QMessageBox(
        QMessageBox.Icon.Question,
        tr("Remove service(s)"),
        tr(
            "Do you want to delete the following {} service(s) from the service file, "
            "or to disable them (comment out)?\n\n{}"
        ).format(len(service_names), "\n".join(service_names)),
        QMessageBox.StandardButton.Cancel,
        parent,
    )
    delete_button = message_box.addButton(tr("Delete"), QMessageBox.ButtonRole.DestructiveRole)
    disable_button = message_box.addButton(
        tr("Disable (comment out)"), QMessageBox.ButtonRole.AcceptRole
    )
    message_box.setDefaultButton(QMessageBox.StandardButton.Cancel)
    message_box.exec()

    if message_box.clickedButton() == delete_button:
        return RemoveAction.DELETE
    if message_box.clickedButton() == disable_button:
        return RemoveAction.DISABLE
    return None
