#!/usr/bin/env python3
"""Take screenshots of the PG Service Parser plugin GUI for documentation.

Usage (inside QGIS Docker):
    QT_SCALE_FACTOR=2 xvfb-run --server-args="-screen 0 3840x2160x24 -dpi 192" python scripts/screenshots.py

Or via the wrapper:
    ./scripts/screenshots.sh

This script bootstraps a headless QgsApplication, creates a temporary
pg_service.conf with sample services, and captures the plugin dialog at
each relevant state.

Screenshots are saved to docs/docs/assets/images/screenshots/.
Only files whose pixels actually changed are overwritten (diffing guard).
"""

import configparser
import sys
import tempfile
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Bootstrap QGIS
# ---------------------------------------------------------------------------
from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QPoint, Qt, QTimer
from qgis.PyQt.QtGui import QColor, QFont, QImage, QPainter, QPen, QPixmap
from qgis.PyQt.QtWidgets import QApplication, QMainWindow

# Start QgsApplication (headless, no GUI prefix)
_qgs = QgsApplication([], True)
_qgs.initQgis()

# Set a consistent default font with anti-aliasing for clean screenshots
_font = QFont("DejaVu Sans", 10)
_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias | QFont.StyleStrategy.PreferQuality)
_font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
_qgs.setFont(_font)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path("docs/docs/assets/images/screenshots")

# Click marker style (consistent with oqtopus)
MARKER_COLOR = QColor(255, 50, 50, 200)
MARKER_RADIUS = 18
MARKER_PEN_WIDTH = 3
MARKER_CROSSHAIR_LEN = 8

# Connection errors by host, so that the screenshots do not depend on the network
CONNECTION_ERRORS = {
    "staging.example.com": (
        'connection to server at "staging.example.com" (203.0.113.10), port 5433 failed: '
        "Connection refused\n"
        "\tIs the server running on that host and accepting TCP/IP connections?"
    ),
    "geoserver.partner.org": (
        'connection to server at "geoserver.partner.org" (198.51.100.7), port 5432 failed: '
        "timeout expired"
    ),
}


# ---------------------------------------------------------------------------
# Minimal iface stub
# ---------------------------------------------------------------------------
class _FakeIface:
    """Minimal QgsInterface stub — just enough for PgServiceDialog."""

    def __init__(self):
        self._main_window = QMainWindow()
        self._main_window.resize(800, 600)

    def mainWindow(self):
        return self._main_window


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _images_differ(path: Path, new_pixmap: QPixmap) -> bool:
    """Return True if the existing image at *path* differs from *new_pixmap*."""
    if not path.exists():
        return True

    existing = QImage(str(path))
    new_img = new_pixmap.toImage()

    if existing.size() != new_img.size():
        return True

    # Compare pixel data
    existing = existing.convertToFormat(QImage.Format.Format_ARGB32)
    new_img = new_img.convertToFormat(QImage.Format.Format_ARGB32)

    for y in range(existing.height()):
        for x in range(existing.width()):
            if existing.pixel(x, y) != new_img.pixel(x, y):
                return True

    return False


def _grab(widget, filename: str, click_targets: list[QPoint] | None = None, popups=None):
    """Grab a screenshot of *widget* and save it (only if changed).

    Args:
        widget: The QWidget to capture.
        filename: File name (e.g. "edit_tab.png").
        click_targets: Optional list of QPoint positions where a click-marker
            circle should be drawn.
        popups: Optional list of popup widgets (e.g. menus) to draw over *widget*,
            as they are separate windows not included in its grab.
    """
    QApplication.processEvents()

    pixmap: QPixmap = widget.grab()

    if popups:
        painter = QPainter(pixmap)
        for popup in popups:
            painter.drawPixmap(widget.mapFromGlobal(popup.mapToGlobal(QPoint(0, 0))), popup.grab())
        painter.end()

    if click_targets:
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(MARKER_COLOR, MARKER_PEN_WIDTH)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        for pt in click_targets:
            painter.drawEllipse(pt, MARKER_RADIUS, MARKER_RADIUS)
            r = MARKER_CROSSHAIR_LEN
            painter.drawLine(pt.x() - r, pt.y(), pt.x() + r, pt.y())
            painter.drawLine(pt.x(), pt.y() - r, pt.x(), pt.y() + r)

        painter.end()

    path = OUTPUT_DIR / filename
    if _images_differ(path, pixmap):
        pixmap.save(str(path))
        print(f"  [updated] {path}")
    else:
        print(f"  [unchanged] {path}")


def _widget_center_in(widget, ancestor) -> QPoint:
    """Return the center of *widget* mapped to *ancestor*'s coordinate system."""
    local_center = QPoint(widget.width() // 2, widget.height() // 2)
    return widget.mapTo(ancestor, local_center)


def _wait_for(condition, timeout: float = 30):
    """Process events until *condition* returns True."""
    deadline = time.monotonic() + timeout
    while not condition():
        if time.monotonic() > deadline:
            raise TimeoutError(f"{condition} still False after {timeout}s")
        QApplication.processEvents()
        time.sleep(0.05)


def _grab_modal_and_click(filename: str, button_text: str):
    """Once the next modal dialog is shown, grab it and click one of its buttons."""

    def grab_and_click():
        dialog = QApplication.activeModalWidget()
        _grab(dialog, filename)
        next(button for button in dialog.buttons() if button.text() == button_text).click()

    QTimer.singleShot(200, grab_and_click)


def _fake_connection_error(params: dict) -> str | None:
    """Connection test returning the errors of CONNECTION_ERRORS."""
    from pg_service_parser.libs.pgserviceparser import service_config

    host = params.get("host") or service_config(params["service"])["host"]
    return CONNECTION_ERRORS.get(host)


def _create_sample_conf(conf_path: Path):
    """Write a sample pg_service.conf with realistic services."""
    config = configparser.ConfigParser()

    config["production"] = {
        "host": "db.example.com",
        "port": "5432",
        "dbname": "cadastre_prod",
        "user": "gis_admin",
        "password": "s3cur3Pa$$w0rd",
        "sslmode": "verify-full",
        "sslrootcert": "/etc/ssl/certs/ca-bundle.crt",
        "sslcert": "/home/gis/.postgresql/client.crt",
        "sslkey": "/home/gis/.postgresql/client.key",
    }
    config["development"] = {
        "host": "localhost",
        "port": "5432",
        "dbname": "cadastre_dev",
        "user": "developer",
        "sslmode": "prefer",
    }
    config["staging"] = {
        "host": "staging.example.com",
        "port": "5433",
        "dbname": "cadastre_staging",
        "user": "deployer",
        "password": "depl0y_2024!",
        "sslmode": "require",
        "sslrootcert": "/etc/ssl/certs/ca-bundle.crt",
    }
    config["external_wfs"] = {
        "host": "geoserver.partner.org",
        "port": "5432",
        "dbname": "shared_geodata",
        "user": "readonly",
        "sslmode": "require",
    }
    config["sketches"] = {
        "host": "localhost",
        "port": "5432",
        "dbname": "sketches",
        "user": "sketcher",
        "sslmode": "disable",
    }

    with open(conf_path, "w") as f:
        config.write(f)


# ---------------------------------------------------------------------------
# Workflow steps
# ---------------------------------------------------------------------------


def step_edit_tab(dlg):
    """Capture the edit tab with a service selected and settings visible."""
    widget = dlg._PgServiceDialog__service_widget

    # Select the "production" service (most populated) for an informative screenshot
    for i in range(widget.lstServices.count()):
        if widget.lstServices.item(i).text() == "production":
            widget.lstServices.setCurrentRow(i)
            break
    else:
        if widget.lstServices.count() > 0:
            widget.lstServices.setCurrentRow(0)

    QApplication.processEvents()
    _grab(dlg, "edit_tab.png")


def step_context_menu(dlg):
    """Capture the context menu on a service (rename / duplicate)."""
    widget = dlg._PgServiceDialog__service_widget

    if widget.lstServices.count() > 0:
        widget.lstServices.setCurrentRow(0)

    QApplication.processEvents()

    # Create the context menu manually (same logic as _service_list_context_menu)
    from qgis.core import QgsApplication as QgsApp
    from qgis.PyQt.QtWidgets import QAction, QMenu

    item = widget.lstServices.item(0)
    if not item:
        print("  [skipped] context_menu.png — no services")
        return

    menu = QMenu(widget)
    rename_action = QAction(
        QgsApp.getThemeIcon("/mActionRename.svg"),
        "Rename service...",
        widget,
    )
    menu.addAction(rename_action)

    duplicate_action = QAction(
        QgsApp.getThemeIcon("/mActionDuplicateLayer.svg"),
        "Duplicate service...",
        widget,
    )
    menu.addAction(duplicate_action)

    # Position the menu near the selected item
    rect = widget.lstServices.visualItemRect(item)
    pos = rect.center()
    global_pos = widget.lstServices.viewport().mapToGlobal(pos)
    menu.popup(global_pos)
    QApplication.processEvents()

    # Grab the dialog with the menu overlaid
    _grab(dlg, "context_menu.png", popups=[menu])
    menu.close()


def step_shortcuts_tab(dlg, shortcuts_model):
    """Capture the shortcuts tab with pre-populated shortcuts."""
    # Add sample shortcuts so the tab isn't empty
    shortcuts_model.add_shortcut("staging", "production")
    shortcuts_model.add_shortcut("development", "staging")

    dlg.tabWidget.setCurrentIndex(1)
    QApplication.processEvents()
    _grab(dlg, "shortcuts_tab.png")

    # Clean up the shortcuts we just added
    while shortcuts_model.rowCount():
        shortcuts_model.remove_shortcut(shortcuts_model.index(0, 0))


def step_connections_tab(dlg):
    """Capture the connections tab."""
    dlg.tabWidget.setCurrentIndex(2)
    QApplication.processEvents()
    _grab(dlg, "connections_tab.png")


def step_test_services(dlg):
    """Capture the test dialog listing the services that could not be connected."""
    from pg_service_parser.gui.dlg_service_test import ServiceTestDialog
    from pg_service_parser.libs.pgserviceparser import service_names

    dlg.tabWidget.setCurrentIndex(0)
    widget = dlg._PgServiceDialog__service_widget

    test_dlg = ServiceTestDialog(widget, service_names())
    test_dlg.show()
    _wait_for(test_dlg.progressBar.isHidden)
    _grab(test_dlg, "test_services.png")
    test_dlg.close()


def step_remove_services(dlg):
    """Disable services and capture the question asked when removing a service."""
    from pg_service_parser.gui.remove_services import RemoveAction
    from pg_service_parser.libs.pgserviceparser import create_service

    widget = dlg._PgServiceDialog__service_widget

    # Disable the services that failed the test
    widget._remove_services(["external_wfs", "staging"], RemoveAction.DISABLE)

    # Remove a service from the main dialog: grab the question and disable it
    widget.lstServices.setCurrentItem(
        widget.lstServices.findItems("sketches", Qt.MatchFlag.MatchExactly)[0]
    )
    _grab_modal_and_click("remove_services.png", "Disable (comment out)")
    widget._remove_service_clicked()

    # A new service with the same name is created, so that the disabled one cannot be restored
    create_service(
        "sketches",
        {"host": "localhost", "port": "5432", "dbname": "sketches_2026", "user": "sketcher"},
    )
    widget._refresh_service_list()


def step_disabled_services(dlg):
    """Capture the edit tab with the button to restore the disabled services."""
    widget = dlg._PgServiceDialog__service_widget

    dlg.bar.clearWidgets()
    widget.lstServices.setCurrentItem(
        widget.lstServices.findItems("production", Qt.MatchFlag.MatchExactly)[0]
    )
    QApplication.processEvents()
    _grab(dlg, "disabled_services.png")


def step_restore_services(dlg):
    """Capture the restore dialog, once the disabled services are tested."""
    from pg_service_parser.gui.dlg_service_restore import ServiceRestoreDialog

    # The partner server is back online
    del CONNECTION_ERRORS["geoserver.partner.org"]

    widget = dlg._PgServiceDialog__service_widget
    restore_dlg = ServiceRestoreDialog(widget, widget._conf_file_path)
    restore_dlg.show()
    _wait_for(restore_dlg.progressBar.isHidden)
    _grab(restore_dlg, "restore_services.png")
    restore_dlg.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    _ensure_output_dir()

    # Create a temporary pg_service.conf with sample data
    tmp_dir = tempfile.mkdtemp()
    conf_file = Path(tmp_dir) / "pg_service.conf"
    _create_sample_conf(conf_file)

    # Point the library to our temp conf file
    import os

    os.environ["PGSERVICEFILE"] = str(conf_file)

    # Import plugin modules (after env is set)
    from pg_service_parser.core import service_tester
    from pg_service_parser.core.copy_shortcuts import ShortcutsModel
    from pg_service_parser.gui.dlg_pg_service import PgServiceDialog
    from pg_service_parser.libs.pgserviceparser import conf_path, service_names

    # Fake the connection test (psycopg is then not needed)
    service_tester.connection_error = _fake_connection_error
    service_tester.psycopg = True

    iface = _FakeIface()

    shortcuts_model = ShortcutsModel(
        iface.mainWindow(),
        service_names_func=lambda: service_names(conf_path(), sorted_alphabetically=True),
    )

    dlg = PgServiceDialog(shortcuts_model, iface)
    dlg.resize(600, 480)
    dlg.show()
    QApplication.processEvents()

    # Show a realistic Windows path instead of the temp directory
    dlg.txtConfFile.setText(r"C:\Users\sketcher\AppData\Roaming\postgresql\pg_service.conf")

    print("Taking screenshots...")

    print("  01 Edit tab...")
    step_edit_tab(dlg)

    print("  02 Context menu...")
    step_context_menu(dlg)

    print("  03 Shortcuts tab...")
    step_shortcuts_tab(dlg, shortcuts_model)

    print("  04 Connections tab...")
    step_connections_tab(dlg)

    print("  05 Test services...")
    step_test_services(dlg)

    print("  06 Remove services...")
    step_remove_services(dlg)

    print("  07 Disabled services...")
    step_disabled_services(dlg)

    print("  08 Restore services...")
    step_restore_services(dlg)

    dlg.close()

    # Cleanup
    conf_file.unlink(missing_ok=True)
    Path(tmp_dir).rmdir()

    _qgs.exitQgis()
    print(f"Done — screenshots in {OUTPUT_DIR}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback

        traceback.print_exc()
        sys.exit(1)
