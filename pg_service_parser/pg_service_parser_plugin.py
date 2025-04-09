import os
from pathlib import Path

from qgis.core import NULL, QgsSettingsTree
from qgis.PyQt.QtCore import QCoreApplication, QLocale, QSettings, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu, QToolButton

from pg_service_parser.core.copy_shortcuts import ShortcutsModel
from pg_service_parser.core.pg_service_parser_wrapper import (
    conf_path,
    copy_service_settings,
    service_names,
)
from pg_service_parser.core.plugin_settings import PLUGIN_NAME
from pg_service_parser.gui.dlg_pg_service import PgServiceDialog


class PgServiceParserPlugin:
    def __init__(self, iface):
        self.iface = iface

        # initialize translation
        qgis_locale = QLocale(
            str(QSettings().value("locale/userLocale")).replace(str(NULL), "en_CH")
        )
        locale_path = os.path.join(os.path.dirname(__file__), "i18n")
        self.translator = QTranslator()
        self.translator.load(qgis_locale, "qgis-pg-service-parser-plugin", "_", locale_path)
        QCoreApplication.installTranslator(self.translator)

        self.action = None
        self.shortcuts_model = None

    def tr(self, text: str) -> str:
        return QCoreApplication.translate("Plugin", text)

    def initGui(self):
        icon = QIcon(str(Path(__file__).parent / "images" / "logo.png"))

        self.default_action = QAction(
            icon,
            "PG service parser",
            self.iface.mainWindow(),
        )
        self.default_action.triggered.connect(self.run)

        self.iface.addPluginToDatabaseMenu("PG service parser", self.default_action)
        self.menu = self.iface.mainWindow().getDatabaseMenu("PG service parser")
        self.menu.setIcon(icon)
        self.menu.setToolTipsVisible(True)

        self.button = QToolButton(self.iface.mainWindow())
        self.button.setIcon(icon)
        self.button.setDefaultAction(self.default_action)
        self.action = self.iface.addToolBarWidget(self.button)

        self.shortcuts_model = ShortcutsModel(self.iface.mainWindow())
        self.shortcuts_model.dataChanged.connect(self.build_menus)

        self.build_menus()

    def build_menus(self):
        _conf_path = conf_path()
        if not _conf_path.exists():
            return

        self.menu.clear()
        self.menu.addAction(self.default_action)

        button_menu = QMenu()
        button_menu.setToolTipsVisible(True)
        button_menu.addAction(self.default_action)

        if len(self.shortcuts_model.shortcuts):
            _services = service_names(_conf_path)
            self.button.setPopupMode(QToolButton.MenuButtonPopup)
            button_menu.addSeparator()
            for shortcut in self.shortcuts_model.shortcuts:
                action = QAction(shortcut.name, self.iface.mainWindow())
                action.setToolTip(
                    self.tr(f"Copy service '{shortcut.service_from}' to '{shortcut.service_to}'.")
                )
                action.setEnabled(
                    _conf_path.exists()
                    and shortcut.service_from in _services
                    and shortcut.service_to in _services
                )
                action.triggered.connect(
                    lambda _triggered, _shortcut=shortcut: self.copy_service(
                        _shortcut.service_from, _shortcut.service_to
                    )
                )
                button_menu.addAction(action)
                self.menu.addAction(action)
        else:
            self.button.setPopupMode(QToolButton.ToolButtonPopupMode.DelayedPopup)

        self.button.setMenu(button_menu)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginDatabaseMenu("PG service parser", self.default_action)
        self.menu.clear()
        del self.menu
        QgsSettingsTree.unregisterPluginTreeNode(PLUGIN_NAME)

    def run(self):
        dlg = PgServiceDialog(self.shortcuts_model, self.iface.mainWindow())
        dlg.exec()

    def copy_service(self, service_from: str, service_to: str):
        _conf_path = conf_path()
        if _conf_path.exists():
            copy_service_settings(service_from, service_to, _conf_path)
            self.iface.messageBar().pushMessage(
                "PG service", f"PG service copied from '{service_from}' to '{service_to}'!"
            )
