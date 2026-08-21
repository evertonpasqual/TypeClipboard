#!/bin/bash
#
# TypeClipboard - instalador para macOS
#
#   ./install.sh
#
# Cria:
#   ~/Library/Application Support/TypeClipboard/   (venv + script)
#   ~/Applications/TypeClipboard.app               (icone clicavel)
#
set -euo pipefail

APP_NAME="TypeClipboard"
BUNDLE_ID="com.evertonpasqualin.typeclipboard"
SUPPORT_DIR="$HOME/Library/Application Support/$APP_NAME"
APP_DIR="$HOME/Applications/$APP_NAME.app"
SCRIPT_URL="https://raw.githubusercontent.com/evertonpasqualin/typeclipboard/main/typeclipboard_gui.py"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

info()  { printf "\033[1;34m==>\033[0m %s\n" "$1"; }
ok()    { printf "\033[1;32m OK\033[0m %s\n" "$1"; }
fail()  { printf "\033[1;31mERRO\033[0m %s\n" "$1" >&2; exit 1; }

[ "$(uname -s)" = "Darwin" ] || fail "Este instalador e apenas para macOS."

# ---------------------------------------------------------------- Python
info "Procurando um Python 3 com Tkinter..."
# Ordem de preferencia: versoes maduras primeiro. O 3.14 e muito novo e algumas
# dependencias nativas do pyautogui ainda quebram nele.
PY=""
for candidate in \
    /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 \
    /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 \
    /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    /opt/homebrew/bin/python3.13 \
    /opt/homebrew/bin/python3.12 \
    /opt/homebrew/bin/python3.11 \
    /opt/homebrew/bin/python3 \
    /usr/local/bin/python3 \
    /Library/Frameworks/Python.framework/Versions/3.1*/bin/python3 \
    "$(command -v python3 2>/dev/null || true)"
do
    [ -x "$candidate" ] || continue
    if "$candidate" -c "import tkinter" >/dev/null 2>&1; then
        PY="$candidate"
        break
    fi
done

if [ -z "$PY" ]; then
    cat >&2 <<'MSG'
Nenhum Python 3 com Tkinter encontrado.

Opcoes:
  1) Instale o Python oficial em https://www.python.org/downloads/macos/
     (ja vem com Tkinter, e a opcao mais simples)
  2) Ou via Homebrew:  brew install python-tk
MSG
    exit 1
fi
ok "Python: $PY ($("$PY" -V))"

# ---------------------------------------------------------------- Arquivos
info "Preparando $SUPPORT_DIR"
mkdir -p "$SUPPORT_DIR"

if [ -f "$SRC_DIR/typeclipboard_gui.py" ]; then
    cp "$SRC_DIR/typeclipboard_gui.py" "$SUPPORT_DIR/typeclipboard_gui.py"
else
    info "Baixando o script do GitHub..."
    curl -fsSL "$SCRIPT_URL" -o "$SUPPORT_DIR/typeclipboard_gui.py" \
        || fail "Nao consegui baixar typeclipboard_gui.py"
fi

# ---------------------------------------------------------------- venv
info "Criando ambiente virtual e instalando dependencias..."
rm -rf "$SUPPORT_DIR/venv"
"$PY" -m venv "$SUPPORT_DIR/venv"
"$SUPPORT_DIR/venv/bin/python" -m pip install --quiet --upgrade pip
"$SUPPORT_DIR/venv/bin/python" -m pip install --quiet pyautogui \
    || fail "Falha ao instalar as dependencias."

info "Testando o app em modo headless..."
if ! "$SUPPORT_DIR/venv/bin/python" -c "import tkinter, pyautogui" 2>"$SUPPORT_DIR/import-test.log"; then
    cat "$SUPPORT_DIR/import-test.log" >&2
    fail "O Python instalado nao consegue carregar tkinter + pyautogui. Tente instalar o Python 3.13 do python.org e rodar de novo."
fi
rm -f "$SUPPORT_DIR/import-test.log"
ok "Dependencias instaladas"

# ---------------------------------------------------------------- .app
info "Criando $APP_DIR"
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/Contents/MacOS" "$APP_DIR/Contents/Resources"

cat > "$APP_DIR/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key><string>$APP_NAME</string>
    <key>CFBundleDisplayName</key><string>$APP_NAME</string>
    <key>CFBundleExecutable</key><string>$APP_NAME</string>
    <key>CFBundleIdentifier</key><string>$BUNDLE_ID</string>
    <key>CFBundleVersion</key><string>1.0.0</string>
    <key>CFBundleShortVersionString</key><string>1.0.0</string>
    <key>CFBundlePackageType</key><string>APPL</string>
    <key>CFBundleIconFile</key><string>AppIcon</string>
    <key>NSHighResolutionCapable</key><true/>
    <key>LSMinimumSystemVersion</key><string>11.0</string>
</dict>
</plist>
PLIST

cat > "$APP_DIR/Contents/MacOS/$APP_NAME" <<'LAUNCHER'
#!/bin/bash
DIR="$HOME/Library/Application Support/TypeClipboard"
LOG="$DIR/last-run.log"
{
  echo "--- $(date) ---"
  "$DIR/venv/bin/python" "$DIR/typeclipboard_gui.py" "$@"
  echo "exit code: $?"
} >>"$LOG" 2>&1
LAUNCHER
chmod +x "$APP_DIR/Contents/MacOS/$APP_NAME"

# icone opcional (icon.png 512x512 na pasta do projeto)
if [ -f "$SRC_DIR/icon.png" ] && command -v iconutil >/dev/null 2>&1; then
    info "Gerando icone..."
    TMP_ICON="$(mktemp -d)/AppIcon.iconset"
    mkdir -p "$TMP_ICON"
    for size in 16 32 128 256 512; do
        sips -z $size $size "$SRC_DIR/icon.png" --out "$TMP_ICON/icon_${size}x${size}.png" >/dev/null
        sips -z $((size*2)) $((size*2)) "$SRC_DIR/icon.png" --out "$TMP_ICON/icon_${size}x${size}@2x.png" >/dev/null
    done
    iconutil -c icns "$TMP_ICON" -o "$APP_DIR/Contents/Resources/AppIcon.icns" 2>/dev/null || true
fi

# assinatura ad-hoc: mantem a permissao de Acessibilidade estavel entre updates
if command -v codesign >/dev/null 2>&1; then
    codesign --force --deep --sign - "$APP_DIR" >/dev/null 2>&1 \
        && ok "App assinado (ad-hoc)" \
        || info "codesign nao aplicado (opcional)"
fi

ok "Instalado em $APP_DIR"

cat <<MSG

--------------------------------------------------------------------
 Instalacao concluida!

 1. Abra o Finder > Ir > Aplicativos (ou ~/Applications)
 2. Clique em $APP_NAME
 3. Na PRIMEIRA execucao, o macOS vai pedir permissao:
      Ajustes do Sistema > Privacidade e Seguranca > Acessibilidade
      -> ative $APP_NAME
    Feche e abra o app de novo depois de autorizar.

 Dica: arraste o app para o Dock para ficar com 1 clique.
--------------------------------------------------------------------
MSG
