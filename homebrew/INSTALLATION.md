# Homebrew Installation Guide

This guide explains how to install Media Converter using Homebrew on macOS.

## Prerequisites

- macOS 10.15 (Catalina) or later
- [Homebrew](https://brew.sh/) installed

## Installation

### Option 1: Install from official tap (recommended)

Once the formula is published to a Homebrew tap:

```bash
brew tap paruff/converter
brew install media-converter
```

### Option 2: Install directly from formula

```bash
brew install homebrew/media-converter.rb
```

### Option 3: Install from local formula

If you have cloned this repository:

```bash
cd /path/to/converter
brew install --build-from-source homebrew/media-converter.rb
```

## Usage

After installation, you can use the converter commands:

```bash
# Command-line interface
converter /path/to/videos

# Graphical user interface
converter-gui
```

## Updating

To update to the latest version:

```bash
brew update
brew upgrade media-converter
```

## Uninstallation

To uninstall:

```bash
brew uninstall media-converter
```

## Dependencies

The formula automatically installs:
- Python 3.12+
- FFmpeg (with ffprobe)
- Required Python packages (tqdm, etc.)

## Troubleshooting

### Formula Not Found

If you get a "formula not found" error, ensure you've tapped the repository:

```bash
brew tap paruff/converter
```

### Permission Issues

If you encounter permission issues, try:

```bash
sudo chown -R $(whoami) /usr/local/bin /usr/local/lib
```

### FFmpeg Issues

If FFmpeg is not working properly:

```bash
brew reinstall ffmpeg
```

## Development Installation

For development, install in editable mode:

```bash
# Install dependencies
brew install python@3.12 ffmpeg

# Clone repository
git clone https://github.com/paruff/converter.git
cd converter

# Install in development mode
pip install -e ".[dev]"
```

## Creating the Formula

To update the Homebrew formula with new versions:

1. Create a new release on GitHub with a tag (e.g., `v0.1.0`)
2. Download the release tarball
3. Calculate the SHA256:
   ```bash
   shasum -a 256 v0.1.0.tar.gz
   ```
4. Update the `url` and `sha256` in `homebrew/media-converter.rb`
5. Test the formula:
   ```bash
   brew install --build-from-source homebrew/media-converter.rb
   brew test media-converter
   brew audit --strict media-converter
   ```

## Publishing to Homebrew

To publish to the official Homebrew repository:

1. Create a tap repository: `homebrew-converter`
2. Add the formula to the tap
3. Users can then install with:
   ```bash
   brew tap paruff/converter
   brew install media-converter
   ```

## Support

For issues related to the Homebrew formula, please open an issue at:
https://github.com/paruff/converter/issues
