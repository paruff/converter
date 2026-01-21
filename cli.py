#!/usr/bin/env python3
"""Command-line interface for Media Converter."""

import argparse
import sys
from pathlib import Path

from config import DEFAULT_SD_BITRATE, LOG_DIR, ORIG_DIR, TMP_DIR
from encode import encode
from ffprobe_utils import probe
from file_classifier import classify_video
from repair import repair_mpeg, repair_wmv, repair_xvid
from smart_mode import smart_scale


def get_bitrate(info: dict) -> int:
    """Extract bitrate from video stream info."""
    br = info["video"].get("bit_rate")
    if not br:
        return DEFAULT_SD_BITRATE
    return int(br)


def convert_file(
    path: Path,
    output_dir: Path | None = None,
    keep_original: bool = False,
    verbose: bool = False,
) -> bool:
    """Convert a single video file.

    Args:
        path: Path to the video file
        output_dir: Optional output directory (default: same as input)
        keep_original: If True, keep the original file
        verbose: If True, print detailed progress

    Returns:
        True if conversion succeeded, False otherwise
    """
    if verbose:
        pass

    # Probe file
    info = probe(path)
    if not info:
        return False

    # Find video stream
    video_streams = [s for s in info["streams"] if s["codec_type"] == "video"]
    if not video_streams:
        return False

    video_stream = video_streams[0]
    codec = classify_video(video_stream)

    if verbose:
        pass

    # Calculate bitrate with smart scaling
    scale = smart_scale({"video": video_stream})
    bitrate = get_bitrate({"video": video_stream})
    target_kbps = int((bitrate / 1000) * scale)

    if verbose:
        pass

    # Repair pipeline
    if codec == "mpeg1":
        if verbose:
            pass
        repaired = repair_mpeg(path)
    elif codec == "wmv":
        if verbose:
            pass
        repaired = repair_wmv(path)
    elif codec == "xvid":
        if verbose:
            pass
        repaired = repair_xvid(path)
    else:
        repaired = path

    # Determine output path
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        out = output_dir / path.with_suffix(".mkv").name
    else:
        out = path.with_suffix(".mkv")

    if verbose:
        pass

    # Encode
    try:
        encode(repaired, out, target_kbps)
    except Exception:
        return False

    # Handle original file
    if not keep_original:
        ORIG_DIR.mkdir(exist_ok=True)
        path.rename(ORIG_DIR / path.name)
        if verbose:
            pass

    if verbose:
        pass

    return True


def convert_directory(
    root: Path,
    recursive: bool = False,
    output_dir: Path | None = None,
    keep_original: bool = False,
    verbose: bool = False,
) -> tuple[int, int]:
    """Convert all video files in a directory.

    Args:
        root: Directory to scan
        recursive: If True, scan subdirectories
        output_dir: Optional output directory
        keep_original: If True, keep original files
        verbose: If True, print detailed progress

    Returns:
        Tuple of (successful_count, failed_count)
    """
    extensions = {".avi", ".mpg", ".mpeg", ".wmv", ".mov"}

    if recursive:
        files = [p for p in root.rglob("*") if p.suffix.lower() in extensions]
    else:
        files = [p for p in root.iterdir() if p.is_file() and p.suffix.lower() in extensions]

    if not files:
        return 0, 0

    success_count = 0
    fail_count = 0

    for path in files:
        if convert_file(path, output_dir, keep_original, verbose):
            success_count += 1
        else:
            fail_count += 1

    return success_count, fail_count


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Media Converter - Repair and encode legacy video formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all videos in current directory
  media-converter

  # Convert specific file
  media-converter video.avi

  # Convert directory with verbose output
  media-converter /path/to/videos -v

  # Recursive conversion with custom output directory
  media-converter /path/to/videos -r -o /path/to/output

  # Keep original files
  media-converter /path/to/videos --keep-original
        """,
    )

    parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        default=Path.cwd(),
        help="Path to video file or directory (default: current directory)",
    )

    parser.add_argument("-o", "--output", type=Path, help="Output directory for converted files")

    parser.add_argument(
        "-r", "--recursive", action="store_true", help="Recursively process subdirectories"
    )

    parser.add_argument(
        "-k",
        "--keep-original",
        action="store_true",
        help="Keep original files (don't move to originals/)",
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    args = parser.parse_args()

    # Create necessary directories
    LOG_DIR.mkdir(exist_ok=True)
    TMP_DIR.mkdir(exist_ok=True)

    # Check if path exists
    if not args.path.exists():
        return 1

    # Process file or directory
    if args.path.is_file():
        success = convert_file(args.path, args.output, args.keep_original, args.verbose)
        return 0 if success else 1
    if args.path.is_dir():
        success_count, fail_count = convert_directory(
            args.path, args.recursive, args.output, args.keep_original, args.verbose
        )

        return 0 if fail_count == 0 else 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
