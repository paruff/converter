import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .config import TMP_DIR
from .file_classifier import classify_video
from .logging_utils import run_subprocess


def repair_mpeg(path: Path, dry_run: bool = False) -> Path:
    """Repair MPEG-1 video stream.

    Args:
        path: Input video path
        dry_run: If True, skip actual repair

    Returns:
        Path to repaired file
    """
    logger = logging.getLogger("converter")
    out = TMP_DIR / (path.stem + "_fixed.mkv")

    if dry_run:
        logger.info(f"[DRY-RUN] Would repair MPEG-1: {path} -> {out}")
        return out

    logger.info(f"Repairing MPEG-1: {path.name}")
    TMP_DIR.mkdir(exist_ok=True)

    run_subprocess(
        [
            "ffmpeg",
            "-y",
            "-fflags",
            "+genpts",
            "-err_detect",
            "ignore_err",
            "-i",
            str(path),
            "-c:v",
            "copy",
            "-c:a",
            "copy",
            str(out),
        ],
        logger=logger,
        check=True,
    )

    logger.info(f"MPEG-1 repair complete: {out.name}")
    return out


def repair_wmv(path: Path, dry_run: bool = False) -> Path:
    """Repair WMV video stream.

    Args:
        path: Input video path
        dry_run: If True, skip actual repair

    Returns:
        Path to repaired file
    """
    logger = logging.getLogger("converter")
    out = TMP_DIR / (path.stem + "_fixed.mkv")

    if dry_run:
        logger.info(f"[DRY-RUN] Would repair WMV: {path} -> {out}")
        return out

    logger.info(f"Repairing WMV: {path.name}")
    TMP_DIR.mkdir(exist_ok=True)

    run_subprocess(
        [
            "ffmpeg",
            "-y",
            "-fflags",
            "+genpts",
            "-err_detect",
            "ignore_err",
            "-i",
            str(path),
            "-c:v",
            "copy",
            "-c:a",
            "copy",
            str(out),
        ],
        logger=logger,
        check=True,
    )

    logger.info(f"WMV repair complete: {out.name}")
    return out


def repair_xvid(path: Path, dry_run: bool = False) -> Path:
    """Repair XviD video stream.

    Args:
        path: Input video path
        dry_run: If True, skip actual repair

    Returns:
        Path to repaired file
    """
    logger = logging.getLogger("converter")
    out = TMP_DIR / (path.stem + "_fixed.avi")

    if dry_run:
        logger.info(f"[DRY-RUN] Would repair XviD: {path} -> {out}")
        return out

    logger.info(f"Repairing XviD: {path.name}")
    TMP_DIR.mkdir(exist_ok=True)

    run_subprocess(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(path),
            "-c",
            "copy",
            "-bsf:v",
            "mpeg4_unpack_bframes",
            str(out),
        ],
        logger=logger,
        check=True,
    )

    logger.info(f"XviD repair complete: {out.name}")
    return out


def repair_mpeg2(path: Path, dry_run: bool = False) -> Path:
    """Repair MPEG-2 video stream.

    Args:
        path: Input video path
        dry_run: If True, skip actual repair

    Returns:
        Path to repaired file
    """
    logger = logging.getLogger("converter")
    out = TMP_DIR / (path.stem + "_fixed.mkv")

    if dry_run:
        logger.info(f"[DRY-RUN] Would repair MPEG-2: {path} -> {out}")
        return out

    logger.info(f"Repairing MPEG-2: {path.name}")
    TMP_DIR.mkdir(exist_ok=True)

    run_subprocess(
        [
            "ffmpeg",
            "-y",
            "-fflags",
            "+genpts",
            "-err_detect",
            "ignore_err",
            "-i",
            str(path),
            "-c:v",
            "copy",
            "-c:a",
            "copy",
            str(out),
        ],
        logger=logger,
        check=True,
    )

    logger.info(f"MPEG-2 repair complete: {out.name}")
    return out


def repair_h264_avi(path: Path, dry_run: bool = False) -> Path:
    """Repair H.264-in-AVI video stream.

    Args:
        path: Input video path
        dry_run: If True, skip actual repair

    Returns:
        Path to repaired file
    """
    logger = logging.getLogger("converter")
    out = TMP_DIR / (path.stem + "_fixed.mkv")

    if dry_run:
        logger.info(f"[DRY-RUN] Would repair H.264-in-AVI: {path} -> {out}")
        return out

    logger.info(f"Repairing H.264-in-AVI: {path.name}")
    TMP_DIR.mkdir(exist_ok=True)

    run_subprocess(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(path),
            "-c:v",
            "copy",
            "-c:a",
            "copy",
            str(out),
        ],
        logger=logger,
        check=True,
    )

    logger.info(f"H.264-in-AVI repair complete: {out.name}")
    return out


class RepairDispatcher:
    """Codec-aware repair dispatcher.

    Selects the appropriate repair function based on video codec metadata.
    Supports: MPEG-1, MPEG-2, WMV3, XviD, and H.264-in-AVI.
    """

    def __init__(self, logger: logging.Logger | None = None) -> None:
        """Initialize RepairDispatcher.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger("converter")
        self._repair_map: dict[str, Callable[[Path, bool], Path]] = {
            "mpeg1": repair_mpeg,
            "mpeg2": repair_mpeg2,
            "wmv": repair_wmv,
            "xvid": repair_xvid,
            "h264": repair_h264_avi,
        }

    def needs_repair(self, codec_type: str) -> bool:
        """Check if a codec type needs repair.

        Args:
            codec_type: Codec type from classify_video

        Returns:
            True if repair is available for this codec
        """
        return codec_type in self._repair_map

    def dispatch(self, path: Path, video_stream: dict[str, Any], dry_run: bool = False) -> Path:
        """Dispatch to appropriate repair function based on codec.

        Args:
            path: Input video path
            video_stream: Video stream metadata from ffprobe
            dry_run: If True, skip actual repair

        Returns:
            Path to repaired file, or original path if no repair needed
        """
        codec_type = classify_video(video_stream)

        if not self.needs_repair(codec_type):
            self.logger.info(f"No repair needed for codec: {codec_type}")
            return path

        repair_func = self._repair_map[codec_type]
        self.logger.info(f"Dispatching repair for codec: {codec_type}")
        return repair_func(path, dry_run)
