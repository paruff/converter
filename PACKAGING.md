# macOS App Packaging Guide

This guide explains how to package Media Converter as a standalone macOS application using PyInstaller.

## Prerequisites

- macOS 10.15 (Catalina) or later
- Python 3.10 or later
- PyInstaller 6.0 or later
- FFmpeg (installed via Homebrew)

## Quick Start

```bash
# Install packaging dependencies
pip install -e ".[packaging]"

# Build the app
./scripts/build_macos.sh

# Create a DMG installer (optional)
./scripts/create_dmg.sh
```

## Detailed Instructions

### 1. Install Dependencies

```bash
# Install FFmpeg if not already installed
brew install ffmpeg

# Install packaging dependencies
pip install pyinstaller>=6.0.0

# Or install all optional dependencies
pip install -e ".[dev,packaging]"
```

### 2. Build the macOS App

The build script handles all the necessary steps:

```bash
./scripts/build_macos.sh
```

This will:
1. Clean previous builds
2. Run PyInstaller with the spec file
3. Create `dist/MediaConverter.app`

### 3. Test the App

```bash
# Run the app from command line
open dist/MediaConverter.app

# Or double-click the app in Finder
```

### 4. Create a DMG Installer (Optional)

To create a distributable DMG file:

```bash
# Install create-dmg tool
brew install create-dmg

# Create the DMG
./scripts/create_dmg.sh
```

This creates `MediaConverter-0.1.0.dmg` that users can download and install.

## Manual Build Process

If you prefer to build manually:

```bash
# Clean previous builds
rm -rf build dist MediaConverter.app

# Build with PyInstaller
pyinstaller MediaConverter.spec --clean --noconfirm

# The app will be in dist/MediaConverter.app
```

## Installation

### For Development/Testing

```bash
# Copy to Applications folder
sudo cp -R dist/MediaConverter.app /Applications/

# Or create a symlink
ln -s "$(pwd)/dist/MediaConverter.app" /Applications/MediaConverter.app
```

### For Distribution

1. Create a DMG using `./scripts/create_dmg.sh`
2. Distribute the DMG file
3. Users can drag the app to their Applications folder

## Customization

### App Icon

To add a custom icon:

1. Create an icon file (`icon.icns`) using `iconutil`:
   ```bash
   # Create iconset directory
   mkdir MyIcon.iconset
   
   # Add icon images at different sizes
   # icon_16x16.png, icon_32x32.png, icon_128x128.png, etc.
   
   # Convert to icns
   iconutil -c icns MyIcon.iconset
   ```

2. Update `MediaConverter.spec`:
   ```python
   app = BUNDLE(
       coll,
       name='MediaConverter.app',
       icon='path/to/icon.icns',  # Add this line
       ...
   )
   ```

### App Bundle Information

Edit `MediaConverter.spec` to customize:
- Bundle identifier
- Version numbers
- Copyright information
- Supported file types
- System requirements

### Hidden Imports

If you add new dependencies, update the `hiddenimports` list in `MediaConverter.spec`:

```python
hiddenimports=[
    'converter.cli',
    'converter.main',
    'your.new.module',  # Add new modules here
    ...
],
```

## Code Signing and Notarization

For distribution outside the Mac App Store, you should sign and notarize the app.

### 1. Code Signing

```bash
# Sign the app
codesign --force --deep --sign "Developer ID Application: Your Name" \
    dist/MediaConverter.app

# Verify signature
codesign --verify --deep --strict --verbose=2 dist/MediaConverter.app
```

### 2. Notarization

```bash
# Create a zip for notarization
ditto -c -k --keepParent dist/MediaConverter.app MediaConverter.zip

# Submit for notarization
xcrun notarytool submit MediaConverter.zip \
    --apple-id "your@email.com" \
    --team-id "YOUR_TEAM_ID" \
    --password "app-specific-password" \
    --wait

# Staple the ticket
xcrun stapler staple dist/MediaConverter.app
```

## Troubleshooting

### App Won't Open

If macOS blocks the app:

1. Open System Preferences → Security & Privacy
2. Click "Open Anyway" for MediaConverter
3. Or right-click the app and select "Open"

### Missing FFmpeg

The app requires FFmpeg to be installed:

```bash
brew install ffmpeg
```

Alternatively, bundle FFmpeg with the app by adding it to the `binaries` list in the spec file.

### Import Errors

If the app fails with import errors:

1. Check `hiddenimports` in `MediaConverter.spec`
2. Add missing modules
3. Rebuild the app

### Large App Size

To reduce app size:

1. Use UPX compression (enabled by default)
2. Exclude unnecessary packages in `MediaConverter.spec`
3. Remove test files and documentation

## File Structure

After building, the app structure will be:

```
MediaConverter.app/
├── Contents/
│   ├── Info.plist              # App metadata
│   ├── MacOS/
│   │   └── MediaConverter      # Main executable
│   ├── Resources/              # Resources and data files
│   └── Frameworks/             # Bundled libraries
```

## Distribution Checklist

Before distributing the app:

- [ ] Test on a clean macOS installation
- [ ] Verify FFmpeg is installed or bundled
- [ ] Test all features (file conversion, GUI, CLI)
- [ ] Sign the app with Developer ID
- [ ] Notarize with Apple
- [ ] Create a DMG installer
- [ ] Test DMG installation on multiple macOS versions
- [ ] Write installation instructions
- [ ] Include system requirements in documentation

## System Requirements

The packaged app requires:

- macOS 10.15 (Catalina) or later
- 64-bit Intel or Apple Silicon
- FFmpeg (installed via Homebrew or bundled)
- ~50 MB disk space for the app
- Additional space for video processing

## Support

For packaging issues, check:
- PyInstaller documentation: https://pyinstaller.org/
- Apple Developer documentation: https://developer.apple.com/

For app-specific issues, open an issue at:
https://github.com/paruff/converter/issues
