# Media Converter Engine

A robust, modular media conversion engine designed to repair, normalize, and encode legacy or corrupted video files for Plex and Samsung TV compatibility.

## Features

- ✅ **Automatic codec detection** (H.264, MPEG-1, MPEG-2, WMV3, XviD)
- ✅ **Smart Mode dynamic bitrate scaling** for optimal quality
- ✅ **Pre-repair pipelines** for:
  - MPEG-1 timestamp and GOP repair
  - WMV packet resync
  - XviD packed B-frame unpacking
- ✅ **Hardware encoding** (VideoToolbox) with libx264 fallback
- ✅ **Command-line interface** with rich options
- ✅ **Graphical user interface** using tkinter
- ✅ **Docker support** for containerized conversion
- ✅ **Comprehensive test suite** with 39 tests and 61% coverage
- ✅ **Clean directory structure**:
  - `logs/` - Log files
  - `originals/` - Original files (moved after conversion)
  - `tmp_fix/` - Temporary repair files

## Project Structure

```
converter/
├── __init__.py           # Package initialization
├── main.py               # Core conversion logic
├── cli.py                # Command-line interface
├── gui.py                # Graphical user interface
├── ffprobe_utils.py      # FFprobe JSON parsing
├── file_classifier.py    # Codec classification
├── smart_mode.py         # Dynamic bitrate scaling
├── repair.py             # Video repair pipelines
├── encode.py             # Encoding logic
├── logging_utils.py      # Logging utilities
├── config.py             # Configuration
├── tests/                # Test suite (39 tests)
├── Dockerfile            # Docker container
├── Makefile              # Build automation
├── pyproject.toml        # Package metadata
└── requirements.txt      # Dependencies
```

## Requirements

- Python 3.10+
- ffmpeg with ffprobe
- Optional: macOS for VideoToolbox hardware encoding

## Installation

### From source

```bash
# Clone the repository
git clone https://github.com/paruff/converter.git
cd converter

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
make install-dev
```

### Using Docker

```bash
# Build Docker image
make docker-build

# Or manually
docker build -t media-converter:latest .
```

## Usage

### Command-Line Interface (CLI)

```bash
# Convert all videos in current directory
python cli.py

# Convert specific file
python cli.py video.avi

# Convert directory with verbose output
python cli.py /path/to/videos -v

# Recursive conversion with custom output directory
python cli.py /path/to/videos -r -o /path/to/output

# Keep original files (don't move to originals/)
python cli.py /path/to/videos --keep-original

# Show help
python cli.py --help
```

### Graphical User Interface (GUI)

```bash
# Launch GUI
python gui.py
```

The GUI provides:
- File/folder browser
- Conversion progress tracking
- Real-time log output
- Success/failure statistics
- Options for recursive processing and keeping originals

### Docker

```bash
# Run conversion on a directory
docker run -it --rm -v /path/to/media:/media media-converter:latest /media

# Interactive mode
docker run -it --rm -v /path/to/media:/media media-converter:latest bash
```

### Python API

```python
from pathlib import Path
from cli import convert_file, convert_directory

# Convert a single file
convert_file(Path("video.avi"), verbose=True)

# Convert all videos in a directory
success, failed = convert_directory(
    Path("/videos"),
    recursive=True,
    keep_original=False,
    verbose=True
)
```

## Development

This project uses:
- **black** - Code formatting
- **ruff** - Linting
- **mypy** - Type checking
- **pytest** - Testing

### Common Commands

```bash
# Install development dependencies
make install-dev

# Run tests
make test

# Run linter
make lint

# Format code
make format

# Type checking
make type-check

# Run all checks (lint + type-check + test)
make check

# Build package
make build

# Clean build artifacts
make clean
```

### Running Tests

```bash
# Run all tests with coverage
pytest tests/ -v --cov

# Or use Makefile
make test
```

## Configuration

Edit `config.py` to customize:

```python
ROOT = Path.cwd()              # Root directory
LOG_DIR = ROOT / "logs"        # Log directory
TMP_DIR = ROOT / "tmp_fix"     # Temporary repair directory
ORIG_DIR = ROOT / "originals"  # Original files directory

DEFAULT_SD_BITRATE = 1_200_000 # Default bitrate for SD content
```

## Supported Formats

**Input formats:**
- `.avi` (XviD, DivX)
- `.mpg`, `.mpeg` (MPEG-1, MPEG-2)
- `.wmv` (WMV3)
- `.mov` (QuickTime)

**Output format:**
- `.mkv` (H.264 video, AAC audio)

## How It Works

1. **Probe** - Analyze video using ffprobe
2. **Classify** - Detect codec type
3. **Repair** - Apply codec-specific repairs if needed
4. **Scale** - Calculate optimal bitrate using Smart Mode
5. **Encode** - Convert to H.264/AAC in MKV container
6. **Archive** - Move original to `originals/` directory

## Contributing

See `.github/copilot-instructions.md` for AI-assisted development guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.
