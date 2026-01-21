import logging
from pathlib import Path

from .config import ORIG_DIR
from .encode import encode
from .ffprobe_utils import probe
from .repair import RepairDispatcher
from .smart_mode import SmartMode


def convert_file(path: Path, dry_run: bool = False) -> None:
    """Convert a video file using smart mode and codec-aware repair.

    Args:
        path: Path to video file
        dry_run: If True, skip actual conversion
    """
    logger = logging.getLogger("converter")
    
    info = probe(path, dry_run=dry_run)
    if not info:
        return

    video_stream = next(s for s in info["streams"] if s["codec_type"] == "video")
    format_info = info.get("format")

    # Initialize SmartMode and RepairDispatcher
    smart_mode = SmartMode(logger=logger)
    repair_dispatcher = RepairDispatcher(logger=logger)

    # Get base bitrate with fallback strategy
    base_bitrate = smart_mode.get_bitrate(video_stream, format_info)
    
    # Scale bitrate using smart mode
    scaled_bitrate = smart_mode.scale_bitrate(video_stream, base_bitrate)
    target_kbps = int(scaled_bitrate / 1000)

    # Codec-aware repair dispatch
    repaired = repair_dispatcher.dispatch(path, video_stream, dry_run=dry_run)

    out = path.with_suffix(".mkv")
    encode(repaired, out, target_kbps, dry_run=dry_run)

    # Move original
    if not dry_run:
        ORIG_DIR.mkdir(exist_ok=True)
        path.rename(ORIG_DIR / path.name)


def convert_directory(root: Path, dry_run: bool = False) -> None:
    """Convert all video files in a directory.

    Args:
        root: Root directory to search
        dry_run: If True, skip actual conversion
    """
    for path in root.iterdir():
        if path.suffix.lower() in {".avi", ".mpg", ".mpeg", ".wmv", ".mov"}:
            convert_file(path, dry_run=dry_run)


if __name__ == "__main__":
    import sys

    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    convert_directory(root)
