import os
from pathlib import Path

from qgis.core import NULL, Qgis, QgsDataSourceUri, QgsProviderRegistry, QgsSettingsTree
from qgis.PyQt.QtCore import QCoreApplication, QLocale, QSettings, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu, QToolButton

from pg_service_parser.core.copy_shortcuts import ShortcutsModel
from pg_service_parser.core.pg_service_parser_wrapper import (
    conf_path,
    copy_service_settings,
    create_service,
    service_config,
    service_names,
)
from pg_service_parser.core.plugin_settings import PLUGIN_NAME
from pg_service_parser.core.service_connections import (
    edit_connection,
    refresh_connections,
)
from pg_service_parser.gui.dlg_new_name import EnumNewName, get_new_name
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
            self.tr("PG service parser"),
            self.iface.mainWindow(),
        )
        self.default_action.triggered.connect(self.run)

        self.iface.addPluginToDatabaseMenu(self.tr("PG service parser"), self.default_action)
        self.menu = self.iface.mainWindow().getDatabaseMenu(self.tr("PG service parser"))
        self.menu.setIcon(icon)
        self.menu.setToolTipsVisible(True)

        self.button = QToolButton(self.iface.mainWindow())
        self.button.setIcon(icon)
        self.button.setDefaultAction(self.default_action)
        self.action = self.iface.addToolBarWidget(self.button)

        self.shortcuts_model = ShortcutsModel(self.iface.mainWindow())
        self.shortcuts_model.dataChanged.connect(self.build_menus)

        self.add_service_action = QAction(
            icon, self.tr("Create PG service from layer connection"), self.iface.mainWindow()
        )
        self.add_service_action.triggered.connect(self.add_service)
        self.register_connection_action = QAction(
            icon, self.tr("Register layer connection as QGIS connection"), self.iface.mainWindow()
        )
        self.register_connection_action.triggered.connect(self.register_connection)
        self.switch_to_service_action = QAction(
            icon, self.tr("Switch layer to PG service"), self.iface.mainWindow()
        )
        self.switch_to_service_action.triggered.connect(self.switch_to_service)

        self.iface.addCustomActionForLayerType(
            self.add_service_action, "", Qgis.LayerType.Vector, True
        )
        self.iface.addCustomActionForLayerType(
            self.register_connection_action, "", Qgis.LayerType.Vector, True
        )
        self.iface.addCustomActionForLayerType(
            self.switch_to_service_action, "", Qgis.LayerType.Vector, True
        )
        self.iface.layerTreeView().currentLayerChanged.connect(self.current_layer_changed)

        self.current_layer_changed(self.iface.activeLayer())

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
            self.button.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            button_menu.addSeparator()
            for shortcut in self.shortcuts_model.shortcuts:
                action = QAction(shortcut.name, self.iface.mainWindow())
                action.setToolTip(
                    self.tr("Copy service '{}' to '{}'.").format(
                        shortcut.service_from, shortcut.service_to
                    )
                )
                action.setEnabled(
                    _conf_path.exists()
                    and shortcut.service_from in _services  # noqa W503
                    and shortcut.service_to in _services  # noqa W503
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
        self.iface.removePluginDatabaseMenu(self.tr("PG service parser"), self.default_action)
        self.iface.layerTreeView().currentLayerChanged.disconnect(self.current_layer_changed)
        self.iface.removeCustomActionForLayerType(self.add_service_action)
        self.iface.removeCustomActionForLayerType(self.register_connection_action)
        self.iface.removeCustomActionForLayerType(self.switch_to_service_action)

        self.menu.clear()
        del self.menu
        QgsSettingsTree.unregisterPluginTreeNode(PLUGIN_NAME)

    def run(self):
        dlg = PgServiceDialog(self.shortcuts_model, self.iface)
        dlg.exec()

    def open(self, service):
        dlg = PgServiceDialog(self.shortcuts_model, self.iface)
        dlg.cboEditService.setCurrentIndex(dlg.cboEditService.findText(service))
        dlg.exec()

    def copy_service(self, service_from: str, service_to: str):
        _conf_path = conf_path()
        if _conf_path.exists():
            copy_service_settings(service_from, service_to, _conf_path)
            self.iface.messageBar().pushMessage(
                self.tr("PG service"),
                self.tr("PG service copied from '{}' to '{}'!").format(service_from, service_to),
            )

    def current_layer_changed(self, layer):
        isPostgres = layer is not None and layer.providerType() == "postgres"
        noService = isPostgres and QgsDataSourceUri(layer.source()).service() == ""
        self.add_service_action.setVisible(noService)
        self.switch_to_service_action.setVisible(noService)

        if isPostgres:
            register_conn = True
            uri = QgsDataSourceUri(layer.source())
            for n, c in (
                QgsProviderRegistry.instance().providerMetadata("postgres").connections().items()
            ):
                curi = QgsDataSourceUri(c.uri())

                if (
                    curi.service() != uri.service()
                    or curi.host() != uri.host()
                    or curi.port() != uri.port()
                    or curi.database() != uri.database()
                    or curi.username() != uri.username()
                    or curi.password() != uri.password()
                    or curi.sslMode() != uri.sslMode()
                ):
                    continue

                register_conn = False
                break
        else:
            register_conn = False

        self.register_connection_action.setVisible(register_conn)

    def add_service(self):
        uri = QgsDataSourceUri(self.iface.activeLayer().source())

        name = get_new_name(EnumNewName.SERVICE, self.iface.mainWindow())
        if name is None:
            return

        settings = {}
        if uri.host() != "":
            settings["host"] = uri.host()
        if uri.port() != "" and uri.port() != "5432":
            settings["port"] = uri.port()
        if uri.database() != "":
            settings["dbname"] = uri.database()
        if uri.username() != "":
            settings["user"] = uri.username()
        if uri.password() != "":
            settings["password"] = uri.password()
        if uri.sslMode() != QgsDataSourceUri.SslPrefer:
            settings["sslmode"] = QgsDataSourceUri.encodeSslMode(uri.sslMode())

        if create_service(name, settings):
            self.open(name)
        else:
            self.iface.messageBar().pushMessage(
                self.tr("PG service"), self.tr("Could not add service {}").format(name)
            )

    def register_connection(self):
        QgsDataSourceUri(self.iface.activeLayer().source())

        name = get_new_name(EnumNewName.CONNECTION, self.iface.mainWindow())
        if name is None:
            return

        provider = QgsProviderRegistry.instance().providerMetadata("postgres")
        conn = provider.createConnection(self.iface.activeLayer().source(), {})
        provider.saveConnection(conn, name)

        edit_connection(name, self.iface.mainWindow())
        refresh_connections(self.iface)

    def switch_to_service(self):
        lyr = self.iface.activeLayer()
        src = lyr.source()
        uri = QgsDataSourceUri(src)
        if uri.service() != "":
            return

        final_dst = src
        final_service = ""

        for name in service_names():
            # remove everything that matches the service and keep the shortest uri

            uri = QgsDataSourceUri(src)
            config = service_config(name)

            uri.setService(name)

            if uri.host() != "" and "host" in config and uri.host() == config["host"]:
                uri.setHost("")

            if uri.port() != "" and "port" in config and uri.port() == config["port"]:
                uri.setPort("")

            sslmode = QgsDataSourceUri.encodeSslMode(uri.sslMode())
            if sslmode != "sslprefer" and "sslmode" in config and sslmode == config["sslmode"]:
                uri.setSslMode(QgsDataSourceUri.SslPrefer)

            if (
                uri.database() != ""
                and "dbname" in config  # noqa W503
                and uri.database() == config["dbname"]  # noqa W503
            ):
                uri.setDatabase("")

            if uri.username() != "" and "user" in config and uri.username() == config["user"]:
                uri.setUsername("")

            if (
                uri.password() != ""
                and "password" in config  # noqa W503
                and uri.password() == config["password"]  # noqa W503
            ):
                uri.setPassword("")

            dst = uri.uri()
            if len(dst) - len(name) < len(final_dst) - len(final_service):
                final_dst = dst
                final_service = name

        if final_dst != "":
            lyr.setDataSource(final_dst)
        else:
            self.iface.messageBar().pushMessage(
                self.tr("PG service"),
                self.tr("No matching service found."),
            )
