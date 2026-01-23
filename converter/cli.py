#!/usr/bin/env python3
"""Command-line interface for Media Converter."""

import argparse
import logging
import shutil
import sys
from pathlib import Path

from .config import DEFAULT_SD_BITRATE, LOG_DIR, MAX_WORKERS, ORIG_DIR, TMP_DIR
from .encode import encode
from .ffprobe_utils import probe
from .file_classifier import classify_video
from .logging_utils import get_file_logger, setup_logging
from .metadata import fetch_and_embed_metadata
from .parallel import ParallelEncoder
from .repair import repair_mpeg, repair_wmv, repair_xvid
from .smart_mode import smart_scale
from .summary import ConversionSummary

# Supported video file extensions
SUPPORTED_EXTENSIONS = {".avi", ".mpg", ".mpeg", ".wmv", ".mov", ".mp4", ".mkv"}


def validate_path(path: Path) -> str | None:
    """Validate input path.

    Args:
        path: Path to validate

    Returns:
        Error message if invalid, None if valid
    """
    if not path.exists():
        return f"Path does not exist: {path}"

    if not path.is_file() and not path.is_dir():
        return f"Path is neither a file nor directory: {path}"

    if path.is_file():
        # Check if file is readable
        try:
            path.stat()
        except PermissionError:
            return f"File is not readable: {path}"

        # Check if supported extension
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return f"Unsupported file type: {path.suffix} (supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))})"

    elif path.is_dir():
        # Check if directory is readable
        try:
            list(path.iterdir())
        except PermissionError:
            return f"Directory is not readable: {path}"

    return None


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
    dry_run: bool = False,
    no_metadata: bool = False,
) -> tuple[bool, bool, str | None, str | None]:
    """Convert a single video file.

    Args:
        path: Path to the video file
        output_dir: Optional output directory (default: same as input)
        keep_original: If True, keep the original file
        verbose: If True, print detailed progress
        dry_run: If True, perform dry run without actual conversion
        no_metadata: If True, skip metadata fetching and embedding

    Returns:
        Tuple of (success, repaired, warning, error)
    """
    logger = logging.getLogger("converter")
    file_logger = get_file_logger(path)

    file_logger.info(f"Starting conversion: {path}")

    repaired = False
    warning = None

    # Validate file
    if not path.exists():
        error = f"File does not exist: {path}"
        logger.error(error)
        return False, False, None, error

    if not path.is_file():
        error = f"Path is not a file: {path}"
        logger.error(error)
        return False, False, None, error

    # Check if readable
    try:
        path.stat()
    except PermissionError:
        error = f"File is not readable: {path}"
        logger.error(error)
        return False, False, None, error

    # Check extension
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        error = f"Unsupported file type: {path.suffix}"
        logger.error(error)
        return False, False, None, error

    logger.debug(f"Probing file: {path.name}")

    # Probe file
    info = probe(path, dry_run=dry_run)
    if not info:
        error = f"Failed to probe file: {path.name}"
        logger.error(error)
        return False, False, None, error

    # Find video stream
    video_streams = [s for s in info["streams"] if s["codec_type"] == "video"]
    if not video_streams:
        error = f"No video stream found in: {path.name}"
        logger.error(error)
        return False, False, None, error

    video_stream = video_streams[0]
    codec = classify_video(video_stream)

    logger.info(f"Detected codec: {codec}")

    # Calculate bitrate with smart scaling
    scale = smart_scale({"video": video_stream})
    bitrate = get_bitrate({"video": video_stream})
    target_kbps = int((bitrate / 1000) * scale)

    logger.info(f"Original bitrate: {bitrate // 1000} kbps")
    logger.info(f"Target bitrate: {target_kbps} kbps (Smart Mode: {scale:.1f}x)")

    # Repair pipeline
    if codec == "mpeg1":
        logger.info("Repair pipeline: MPEG-1")
        repaired_path = repair_mpeg(path, dry_run=dry_run)
        repaired = True
    elif codec == "wmv":
        logger.info("Repair pipeline: WMV")
        repaired_path = repair_wmv(path, dry_run=dry_run)
        repaired = True
    elif codec == "xvid":
        logger.info("Repair pipeline: XviD")
        repaired_path = repair_xvid(path, dry_run=dry_run)
        repaired = True
    else:
        logger.info("No repair needed")
        repaired_path = path

    # Determine output path
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        out = output_dir / path.with_suffix(".mkv").name
    else:
        # Write into same directory, but avoid overwriting input
        out = path.with_suffix(".mkv")
        if out == path:
            # Input is already .mkv → append suffix
            out = path.with_name(path.stem + "_converted.mkv")

    logger.info(f"Output: {out}")

    # Encode
    try:
        encode(repaired_path, out, target_kbps, dry_run=dry_run)
    except Exception as e:
        error = f"Encoding failed: {e}"
        logger.exception(error)
        return False, repaired, None, error

    # Embed metadata (after encoding, before moving original)
    if not no_metadata and out.suffix.lower() == ".mkv":
        logger.info("Fetching and embedding metadata...")
        try:
            fetch_and_embed_metadata(out, dry_run=dry_run)
        except Exception as e:
            # Don't fail the conversion if metadata embedding fails
            logger.warning(f"Metadata embedding failed: {e}")

    # Handle original file
    if not dry_run and not keep_original:
        ORIG_DIR.mkdir(exist_ok=True)
        shutil.move(str(path), str(ORIG_DIR / path.name))
        logger.info("Moved original to originals/")
    elif dry_run and not keep_original:
        logger.info("[DRY-RUN] Would move original to originals/")

    logger.info(f"✓ Successfully converted to {out.name}")

    return True, repaired, warning, None


def convert_directory(
    root: Path,
    recursive: bool = False,
    output_dir: Path | None = None,
    keep_original: bool = False,
    verbose: bool = False,
    dry_run: bool = False,
    parallel: bool = True,
    max_workers: int | None = None,
    show_progress: bool = True,
    no_metadata: bool = False,
) -> tuple[int, int]:
    """Convert all video files in a directory.

    Args:
        root: Directory to scan
        recursive: If True, scan subdirectories
        output_dir: Optional output directory
        keep_original: If True, keep original files
        verbose: If True, print detailed progress
        dry_run: If True, perform dry run without actual conversion
        parallel: If True, use parallel encoding (default: True)
        max_workers: Number of parallel workers (default: from config)
        show_progress: If True, show progress bars (default: True)
        no_metadata: If True, skip metadata fetching and embedding

    Returns:
        Tuple of (successful_count, failed_count)
    """
    logger = logging.getLogger("converter")

    logger.info(f"Scanning directory: {root}")

    if recursive:
        files = [p for p in root.rglob("*") if p.suffix.lower() in SUPPORTED_EXTENSIONS]
    else:
        files = [
            p for p in root.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
        ]

    if not files:
        logger.warning("No video files found")
        return 0, 0

    logger.info(f"Found {len(files)} video file{'s' if len(files) != 1 else ''}")

    # Create summary tracker
    summary = ConversionSummary()

    # Use parallel encoding if enabled and more than 1 file
    if parallel and len(files) > 1:
        encoder = ParallelEncoder(
            max_workers=max_workers, logger=logger, show_progress=show_progress
        )

        def convert_wrapper(path: Path) -> bool:
            """Wrapper for convert_file to use with parallel encoder."""
            success, repaired, warning, error = convert_file(
                path, output_dir, keep_original, verbose, dry_run, no_metadata
            )
            summary.add_result(path, success, repaired, warning, error)
            return success

        def progress_callback(path: Path, success: bool) -> None:
            """Callback to log progress."""
            if success:
                logger.info(f"✓ Completed: {path.name}")
            else:
                logger.error(f"✗ Failed: {path.name}")

        success_count, fail_count = encoder.process_files(files, convert_wrapper, progress_callback)
    else:
        # Sequential processing
        if not parallel:
            logger.info("Parallel encoding disabled, using sequential processing")

        success_count = 0
        fail_count = 0

        for idx, path in enumerate(files, 1):
            logger.info(f"Processing file {idx} of {len(files)}: {path.name}")
            success, repaired, warning, error = convert_file(
                path, output_dir, keep_original, verbose, dry_run, no_metadata
            )
            summary.add_result(path, success, repaired, warning, error)
            if success:
                success_count += 1
            else:
                fail_count += 1

    # Print detailed summary
    summary_text = summary.format_summary(LOG_DIR, ORIG_DIR, TMP_DIR)
    logger.info(summary_text)

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

  # Dry run to see what would be done
  media-converter /path/to/videos --dry-run
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

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode - show what would be done without executing",
    )

    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Disable parallel encoding (process files sequentially)",
    )

    parser.add_argument(
        "-j",
        "--workers",
        type=int,
        default=None,
        help=f"Number of parallel workers (default: {MAX_WORKERS})",
    )

    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bars",
    )

    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Disable metadata fetching and embedding",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(verbose=args.verbose)

    logger.info("Media Converter v0.1.0")

    if args.dry_run:
        logger.info("DRY-RUN MODE ENABLED - No files will be modified")

    logger.debug(f"Input: {args.path}")
    if args.output:
        logger.debug(f"Output: {args.output}")
    else:
        logger.debug("Output: (same as input)")
    logger.debug(f"Recursive: {'Yes' if args.recursive else 'No'}")
    logger.debug(f"Keep Original: {'Yes' if args.keep_original else 'No'}")
    logger.debug(f"Parallel: {'No' if args.no_parallel else 'Yes'}")
    if not args.no_parallel and args.workers:
        logger.debug(f"Workers: {args.workers}")
    elif not args.no_parallel:
        logger.debug(f"Workers: {MAX_WORKERS} (default)")

    # Create necessary directories
    LOG_DIR.mkdir(exist_ok=True)
    if not args.dry_run:
        TMP_DIR.mkdir(exist_ok=True)

    # Validate input path
    error = validate_path(args.path)
    if error:
        logger.error(error)
        return 1

    # Process file or directory
    if args.path.is_file():
        logger.info(f"Processing single file: {args.path.name}")
        success, repaired, warning, error = convert_file(
            args.path,
            args.output,
            args.keep_original,
            args.verbose,
            args.dry_run,
            args.no_metadata,
        )

        # Display summary for single file
        summary = ConversionSummary()
        summary.add_result(args.path, success, repaired, warning, error)
        summary_text = summary.format_summary(LOG_DIR, ORIG_DIR, TMP_DIR)
        logger.info(summary_text)

        if success:
            return 0
        logger.error(f"✗ Failed to convert {args.path.name}")
        return 1

    if args.path.is_dir():
        # Check if directory is empty
        try:
            files = [
                p
                for p in args.path.iterdir()
                if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
            ]
            if not files and not args.recursive:
                logger.warning(f"No supported video files found in {args.path}")
                logger.info(f"Supported extensions: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")
                logger.info("Use --recursive to search subdirectories")
                return 1
        except PermissionError:
            logger.error(f"Cannot read directory: {args.path}")
            return 1

        success_count, fail_count = convert_directory(
            args.path,
            args.recursive,
            args.output,
            args.keep_original,
            args.verbose,
            args.dry_run,
            parallel=not args.no_parallel,
            max_workers=args.workers,
            show_progress=not args.no_progress,
            no_metadata=args.no_metadata,
        )

        return 0 if fail_count == 0 else 1

    logger.error(f"Invalid path: {args.path}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
