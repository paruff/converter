# Quick Start Guide

This guide will help you get started with Media Converter in 5 minutes.

## Installation

### Option 1: Python (Recommended for development)

```bash
# Clone the repository
git clone https://github.com/paruff/converter.git
cd converter

# Install dependencies
pip install -r requirements.txt

# Verify installation
python cli.py --version
```

### Option 2: Docker (Recommended for production)

```bash
# Build the Docker image
docker build -t media-converter:latest .

# Verify installation
docker run --rm media-converter:latest --version
```

## Basic Usage

### Convert a Single File

```bash
# Using Python
python cli.py /path/to/video.avi -v

# Using Docker
docker run -v /path/to:/media media-converter:latest /media/video.avi -v
```

### Convert a Directory

```bash
# Using Python
python cli.py /path/to/videos -r -v

# Using Docker
docker run -v /path/to/videos:/media media-converter:latest /media -r -v
```

### GUI Mode

```bash
# Launch the graphical interface
python gui.py
```

Then:
1. Click "Browse File" or "Browse Folder"
2. Select your video files
3. (Optional) Choose output directory
4. (Optional) Enable recursive processing
5. Click "Start Conversion"
6. Monitor progress in real-time

## Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `-v, --verbose` | Show detailed progress | `python cli.py video.avi -v` |
| `-r, --recursive` | Process subdirectories | `python cli.py /videos -r` |
| `-o, --output DIR` | Custom output directory | `python cli.py video.avi -o /output` |
| `-k, --keep-original` | Keep original files | `python cli.py video.avi -k` |

## What Gets Converted?

**Supported formats:**
- `.avi` (XviD, DivX)
- `.mpg`, `.mpeg` (MPEG-1, MPEG-2)
- `.wmv` (WMV3)
- `.mov` (QuickTime)

**Output format:**
- `.mkv` with H.264 video and AAC audio

## Directory Structure After Conversion

```
your-media-folder/
├── video1.mkv          # Converted files
├── video2.mkv
├── originals/          # Original files moved here
│   ├── video1.avi
│   └── video2.wmv
├── logs/               # Conversion logs
└── tmp_fix/            # Temporary repair files (auto-cleaned)
```

## Examples

### Example 1: Convert Current Directory

```bash
# Convert all videos in current directory
python cli.py
```

### Example 2: Batch Convert with Custom Output

```bash
# Convert entire folder tree to separate output directory
python cli.py /media/old-videos -r -o /media/converted -v
```

### Example 3: Keep Originals

```bash
# Convert but keep original files
python cli.py /media/videos -k
```

### Example 4: Docker Batch Conversion

```bash
# Convert entire directory with Docker
docker run -v /path/to/media:/media media-converter:latest /media -r -v
```

## Troubleshooting

### FFmpeg Not Found

**Error:** `ffmpeg: command not found`

**Solution:**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Docker (already included)
docker run ... media-converter:latest ...
```

### No Video Files Found

**Error:** `No video files found in /path/to/dir`

**Check:**
1. Correct directory path
2. Supported file extensions (`.avi`, `.mpg`, `.wmv`, `.mov`)
3. Use `-r` flag for subdirectories

### Conversion Failed

**Error:** `ERROR: Encoding failed for video.avi`

**Debug:**
```bash
# Run with verbose output
python cli.py video.avi -v

# Check logs directory
cat logs/conversion.log
```

## Next Steps

- Read the full [README](README.md) for advanced features
- Check [CONTRIBUTING.md](CONTRIBUTING.md) if you want to contribute
- See [Documentation](README.md#how-it-works) for technical details

## Getting Help

- 📖 Check the [README](README.md)
- 🐛 Report bugs via [GitHub Issues](https://github.com/paruff/converter/issues)
- 💬 Ask questions in [Discussions](https://github.com/paruff/converter/discussions)
