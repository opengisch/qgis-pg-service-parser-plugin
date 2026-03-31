#!/usr/bin/env bash
# Generate documentation screenshots using QGIS Docker.
#
# Usage:
#   ./scripts/screenshots.sh
#
# Requirements:
#   - Docker installed and running.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

docker run --rm \
    --platform linux/amd64 \
    -v "$REPO_DIR":/app \
    -w /app \
    qgis/qgis:latest \
    bash -c '
        apt-get update -qq &&
        apt-get install -y -qq xvfb fonts-dejavu fonts-liberation fontconfig > /dev/null 2>&1 &&
        pip install --break-system-packages -q -r requirements.txt &&
        # Make pgserviceparser available as pg_service_parser.libs.pgserviceparser
        site_pkg=$(python3 -c "import pgserviceparser; import os; print(os.path.dirname(pgserviceparser.__file__))") &&
        ln -sfn "$site_pkg" /app/pg_service_parser/libs/pgserviceparser &&

        # Enable font anti-aliasing and hinting via fontconfig
        mkdir -p /etc/fonts/conf.d
        cat > /etc/fonts/local.conf <<EOF
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <match target="font">
    <edit name="antialias" mode="assign"><bool>true</bool></edit>
    <edit name="hinting" mode="assign"><bool>true</bool></edit>
    <edit name="hintstyle" mode="assign"><const>hintslight</const></edit>
    <edit name="rgba" mode="assign"><const>rgb</const></edit>
    <edit name="lcdfilter" mode="assign"><const>lcddefault</const></edit>
  </match>
</fontconfig>
EOF
        fc-cache -f > /dev/null 2>&1

        # Use Xvfb with 2x scale for crisp text rendering
        export QT_QPA_PLATFORM=xcb
        export QT_STYLE_OVERRIDE=Fusion
        export QT_SCALE_FACTOR=2
        export QT_FONT_DPI=96
        PYTHONPATH=/app:$PYTHONPATH xvfb-run --server-args="-screen 0 3840x2160x24 -dpi 192" python3 scripts/screenshots.py
    '
