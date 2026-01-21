#!/usr/bin/env bash
# Script to create a DMG installer for Media Converter

set -e

APP_NAME="MediaConverter"
VERSION="0.1.0"
DMG_NAME="${APP_NAME}-${VERSION}.dmg"
APP_PATH="dist/${APP_NAME}.app"

echo "=========================================="
echo "Creating DMG installer for ${APP_NAME}"
echo "=========================================="
echo ""

# Check if app exists
if [ ! -d "$APP_PATH" ]; then
    echo "Error: App not found at $APP_PATH"
    echo "Please run ./scripts/build_macos.sh first"
    exit 1
fi

# Check if create-dmg is installed
if ! command -v create-dmg &> /dev/null; then
    echo "create-dmg not found. Installing via Homebrew..."
    brew install create-dmg
fi

# Clean previous DMG
rm -f "${DMG_NAME}"

echo "Creating DMG..."
create-dmg \
    --volname "${APP_NAME}" \
    --volicon "${APP_PATH}/Contents/Resources/icon.icns" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "${APP_NAME}.app" 175 120 \
    --hide-extension "${APP_NAME}.app" \
    --app-drop-link 425 120 \
    "${DMG_NAME}" \
    "$APP_PATH" || true  # create-dmg returns non-zero even on success

if [ -f "${DMG_NAME}" ]; then
    echo ""
    echo "✓ DMG created successfully: ${DMG_NAME}"
    echo ""
    echo "You can now distribute this DMG file."
    echo "Users can drag the app to their Applications folder."
else
    echo ""
    echo "✗ Failed to create DMG"
    exit 1
fi
