from qgis.core import QgsSettingsEntryString, QgsSettingsTree

PLUGIN_NAME = "pg_service_parser"


class PluginSettings:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)

            settings_node = QgsSettingsTree.createPluginTreeNode(pluginName=PLUGIN_NAME)
            shortcuts_node = settings_node.createNamedListNode("shortcuts")

            cls.shortcut_from = QgsSettingsEntryString("shortcut_from", shortcuts_node)
            cls.shortcut_to = QgsSettingsEntryString("shortcut_to", shortcuts_node)
            cls.shortcuts_node = shortcuts_node

        return cls.instance
