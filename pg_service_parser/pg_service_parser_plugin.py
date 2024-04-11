from qgis.PyQt.QtWidgets import QAction

from pg_service_parser.gui.dlg_pg_service import PgServiceDialog


class PgServiceParserPlugin():
    def __init__(self, iface):
        self.iface = iface
        self.action = None

    def initGui(self):
        self.action = QAction('Go!', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        dlg = PgServiceDialog(self.iface.mainWindow())
        dlg.exec_()
