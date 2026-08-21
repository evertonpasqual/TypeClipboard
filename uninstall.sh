#!/bin/bash
# TypeClipboard - desinstalador
set -euo pipefail

APP_NAME="TypeClipboard"
SUPPORT_DIR="$HOME/Library/Application Support/$APP_NAME"
APP_DIR="$HOME/Applications/$APP_NAME.app"

echo "Removendo $APP_DIR"
rm -rf "$APP_DIR"

echo "Removendo $SUPPORT_DIR"
rm -rf "$SUPPORT_DIR"

echo "Pronto. Se quiser, remova tambem a entrada do app em"
echo "Ajustes do Sistema > Privacidade e Seguranca > Acessibilidade."
