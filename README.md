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
- ✅ **Parallel encoding** with configurable worker threads
- ✅ **Progress bars** with tqdm for real-time feedback
- ✅ **Command-line interface** with rich options
- ✅ **Graphical user interface** using tkinter
- ✅ **Docker support** for containerized conversion
- ✅ **Homebrew formula** for easy installation on macOS
- ✅ **macOS app bundle** packaging with PyInstaller
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
├── parallel.py           # Parallel encoding with ThreadPoolExecutor
├── progress.py           # Progress tracking with tqdm
├── ffprobe_utils.py      # FFprobe JSON parsing
├── file_classifier.py    # Codec classification
├── smart_mode.py         # Dynamic bitrate scaling
├── repair.py             # Video repair pipelines
├── encode.py             # Encoding logic
├── logging_utils.py      # Logging utilities
├── config.py             # Configuration
├── tests/                # Test suite (39 tests)
├── homebrew/             # Homebrew formula
├── scripts/              # Build and packaging scripts
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

### From Homebrew (macOS)

```bash
# Install from Homebrew tap (when published)
brew tap paruff/converter
brew install media-converter

# Or install directly from formula
brew install homebrew/media-converter.rb
```

See [homebrew/INSTALLATION.md](homebrew/INSTALLATION.md) for detailed Homebrew installation instructions.

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

### As macOS App

Download the `.dmg` installer from the releases page and drag the app to your Applications folder.

Or build from source:

```bash
# Install packaging dependencies
pip install -e ".[packaging]"

# Build the app
./scripts/build_macos.sh

# Create DMG installer
./scripts/create_dmg.sh
```

See [PACKAGING.md](PACKAGING.md) for detailed packaging instructions.

## Usage

### Command-Line Interface (CLI)

```bash
# Convert all videos in current directory
converter

# Convert specific file
converter video.avi

# Convert directory with verbose output
converter /path/to/videos -v

# Recursive conversion with custom output directory
converter /path/to/videos -r -o /path/to/output

# Keep original files (don't move to originals/)
converter /path/to/videos --keep-original

# Use parallel encoding with 8 workers
converter /path/to/videos -j 8

# Disable parallel encoding
converter /path/to/videos --no-parallel

# Disable progress bars
converter /path/to/videos --no-progress

# Dry run (see what would be done without executing)
converter /path/to/videos --dry-run

# Show help
converter --help
```

### Graphical User Interface (GUI)

```bash
# Launch GUI
converter-gui
```

The GUI provides:
- File/folder browser
- Parallel encoding with configurable worker count (1-16 threads)
- Real-time progress bars showing current file and overall progress
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
from converter.cli import convert_file, convert_directory

# Convert a single file
convert_file(Path("video.avi"), verbose=True)

# Convert all videos in a directory with parallel encoding
success, failed = convert_directory(
    Path("/videos"),
    recursive=True,
    keep_original=False,
    verbose=True,
    parallel=True,
    max_workers=4,
    show_progress=True
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
MAX_WORKERS = 4                # Default parallel worker count
```

Or use environment variables:

```bash
# Set max workers for parallel encoding
export CONVERTER_MAX_WORKERS=8

# Run with custom worker count
converter /path/to/videos
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
