# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Media Converter macOS app."""

block_cipher = None

# Analysis: collect all Python files and dependencies
a = Analysis(
    ['converter/gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'converter.cli',
        'converter.main',
        'converter.encode',
        'converter.repair',
        'converter.smart_mode',
        'converter.ffprobe_utils',
        'converter.file_classifier',
        'converter.logging_utils',
        'converter.parallel',
        'converter.progress',
        'converter.config',
        'tqdm',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest',
        'pytest-cov',
        'black',
        'ruff',
        'mypy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove test files
a.datas = [x for x in a.datas if not x[0].startswith('tests/')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MediaConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window for GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MediaConverter',
)

# Create macOS app bundle
app = BUNDLE(
    coll,
    name='MediaConverter.app',
    icon=None,  # Add icon path here if available
    bundle_identifier='com.paruff.mediaconverter',
    version='0.1.0',
    info_plist={
        'CFBundleName': 'Media Converter',
        'CFBundleDisplayName': 'Media Converter',
        'CFBundleShortVersionString': '0.1.0',
        'CFBundleVersion': '0.1.0',
        'CFBundleExecutable': 'MediaConverter',
        'CFBundleIdentifier': 'com.paruff.mediaconverter',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'NSHumanReadableCopyright': 'Copyright © 2024 Media Converter Team',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15.0',
        'NSRequiresAquaSystemAppearance': False,
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Video File',
                'CFBundleTypeRole': 'Editor',
                'LSItemContentTypes': [
                    'public.avi',
                    'public.mpeg',
                    'com.microsoft.windows-media-wmv',
                    'com.apple.quicktime-movie',
                ],
            }
        ],
    },
)
