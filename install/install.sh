#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

LOCAL_BIN_DIR="$HOME/.local/bin"
AUTOSTART_DIR="$HOME/.config/autostart"
AUTOSTART_FILE="$AUTOSTART_DIR/deej-mixer.desktop"

MIXER_SRC="$SCRIPT_DIR/deej-mixer"
DEEJ_SRC="$SCRIPT_DIR/deej"
CONFIG_SRC="$SCRIPT_DIR/config.yaml"

# Fallback: if install/deej-mixer is not present, use dist/deej-mixer from the project.
if [[ ! -f "$MIXER_SRC" ]]; then
    MIXER_SRC="$PROJECT_DIR/dist/deej-mixer"
fi

if [[ ! -f "$MIXER_SRC" ]]; then
    echo "Error: deej-mixer binary not found in install/ or dist/." >&2
    exit 1
fi

if [[ ! -f "$DEEJ_SRC" ]]; then
    echo "Error: deej binary not found at $DEEJ_SRC." >&2
    exit 1
fi

if [[ ! -f "$CONFIG_SRC" ]]; then
    echo "Error: config.yaml not found at $CONFIG_SRC." >&2
    exit 1
fi

mkdir -p "$LOCAL_BIN_DIR"
mkdir -p "$AUTOSTART_DIR"

install -m 755 "$MIXER_SRC" "$LOCAL_BIN_DIR/deej-mixer"
install -m 755 "$DEEJ_SRC" "$LOCAL_BIN_DIR/deej"
install -m 644 "$CONFIG_SRC" "$LOCAL_BIN_DIR/config.yaml"

cat > "$AUTOSTART_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Deej Mixer
Exec=$LOCAL_BIN_DIR/deej-mixer
Path=$LOCAL_BIN_DIR/
Terminal=false
StartupNotify=false
X-GNOME-Autostart-enabled=true
EOF

chmod +x "$AUTOSTART_FILE"

echo "Installed successfully."
echo "Binary: $LOCAL_BIN_DIR/deej-mixer"
echo "deej: $LOCAL_BIN_DIR/deej"
echo "Config: $LOCAL_BIN_DIR/config.yaml"
echo "Autostart: $AUTOSTART_FILE"
