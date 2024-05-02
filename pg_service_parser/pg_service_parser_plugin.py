from pathlib import Path

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from pg_service_parser.gui.dlg_pg_service import PgServiceDialog


class PgServiceParserPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None

    def initGui(self):
        self.action = QAction(
            QIcon(str(Path(__file__).parent / "images" / "logo.png")),
            "PG service parser",
            self.iface.mainWindow(),
        )
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToDatabaseMenu("PG service parser", self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginDatabaseMenu("PG service parser", self.action)

    def run(self):
        dlg = PgServiceDialog(self.iface.mainWindow())
        dlg.exec_()
