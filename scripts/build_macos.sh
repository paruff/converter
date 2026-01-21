#!/usr/bin/env bash
# Build script for creating macOS app bundle using PyInstaller

set -e  # Exit on error

echo "=========================================="
echo "Media Converter - macOS App Build Script"
echo "=========================================="
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Warning: This script is designed for macOS."
    echo "The build may not work correctly on other platforms."
    echo ""
fi

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller>=6.0.0
fi

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "Warning: ffmpeg not found in PATH."
    echo "The app will require ffmpeg to be installed separately."
    echo "Install with: brew install ffmpeg"
    echo ""
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist MediaConverter.app
echo "✓ Cleaned"
echo ""

# Build the app
echo "Building macOS app bundle..."
pyinstaller MediaConverter.spec --clean --noconfirm

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Build successful!"
    echo ""
    echo "App location: dist/MediaConverter.app"
    echo ""
    echo "To install the app:"
    echo "  1. Copy dist/MediaConverter.app to /Applications/"
    echo "  2. Or run: sudo cp -R dist/MediaConverter.app /Applications/"
    echo ""
    echo "To create a DMG installer:"
    echo "  brew install create-dmg"
    echo "  ./scripts/create_dmg.sh"
    echo ""
else
    echo ""
    echo "✗ Build failed!"
    exit 1
fi
