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
        print("  Probing file...")

    # Probe file
    info = probe(path)
    if not info:
        print(f"  ✗ Failed to probe file: {path.name}")
        return False

    # Find video stream
    video_streams = [s for s in info["streams"] if s["codec_type"] == "video"]
    if not video_streams:
        print(f"  ✗ No video stream found in: {path.name}")
        return False

    video_stream = video_streams[0]
    codec = classify_video(video_stream)

    if verbose:
        print(f"  Detected codec: {codec}")

    # Calculate bitrate with smart scaling
    scale = smart_scale({"video": video_stream})
    bitrate = get_bitrate({"video": video_stream})
    target_kbps = int((bitrate / 1000) * scale)

    if verbose:
        print(f"  Original bitrate: {bitrate // 1000} kbps")
        print(f"  Target bitrate: {target_kbps} kbps (Smart Mode: {scale}x)")

    # Repair pipeline
    if codec == "mpeg1":
        if verbose:
            print("  Repairing MPEG-1 stream...")
        repaired = repair_mpeg(path)
    elif codec == "wmv":
        if verbose:
            print("  Repairing WMV stream...")
        repaired = repair_wmv(path)
    elif codec == "xvid":
        if verbose:
            print("  Repairing XviD stream...")
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
        print("  Encoding to MKV...")

    # Encode
    try:
        encode(repaired, out, target_kbps)
    except Exception as e:
        print(f"  ✗ Encoding failed: {e}")
        return False

    # Handle original file
    if not keep_original:
        ORIG_DIR.mkdir(exist_ok=True)
        path.rename(ORIG_DIR / path.name)
        if verbose:
            print("  Moved original to originals/")

    if verbose:
        print(f"  ✓ Successfully converted to {out.name}")

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
    if verbose:
        print(f"\nScanning directory: {root}")

    extensions = {".avi", ".mpg", ".mpeg", ".wmv", ".mov"}

    if recursive:
        files = [p for p in root.rglob("*") if p.suffix.lower() in extensions]
    else:
        files = [p for p in root.iterdir() if p.is_file() and p.suffix.lower() in extensions]

    if not files:
        if verbose:
            print("No video files found")
        return 0, 0

    print(f"Found {len(files)} video file{'s' if len(files) != 1 else ''}")

    success_count = 0
    fail_count = 0

    for idx, path in enumerate(files, 1):
        if verbose:
            print(f"\nProcessing file {idx} of {len(files)}: {path.name}")
        if convert_file(path, output_dir, keep_original, verbose):
            success_count += 1
        else:
            fail_count += 1

    # Print summary
    print("\nConversion complete!")
    print(f"Success: {success_count} file{'s' if success_count != 1 else ''}")
    if fail_count > 0:
        print(f"Failed: {fail_count} file{'s' if fail_count != 1 else ''}")

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

    # Print welcome message
    print("Media Converter v0.1.0")

    if args.verbose:
        print(f"Input: {args.path}")
        if args.output:
            print(f"Output: {args.output}")
        else:
            print("Output: (same as input)")
        print(f"Recursive: {'Yes' if args.recursive else 'No'}")
        print(f"Keep Original: {'Yes' if args.keep_original else 'No'}")

    # Create necessary directories
    LOG_DIR.mkdir(exist_ok=True)
    TMP_DIR.mkdir(exist_ok=True)

    # Check if path exists
    if not args.path.exists():
        print(f"Error: Path does not exist: {args.path}")
        return 1

    # Process file or directory
    if args.path.is_file():
        if args.verbose:
            print(f"\nProcessing single file: {args.path.name}")
        success = convert_file(args.path, args.output, args.keep_original, args.verbose)
        if success:
            if not args.verbose:
                print(f"✓ Successfully converted {args.path.name}")
            return 0
        print(f"✗ Failed to convert {args.path.name}")
        return 1
    if args.path.is_dir():
        success_count, fail_count = convert_directory(
            args.path, args.recursive, args.output, args.keep_original, args.verbose
        )

        return 0 if fail_count == 0 else 1

    print(f"Error: Invalid path: {args.path}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
