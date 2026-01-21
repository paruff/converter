"""Progress tracking utilities using tqdm."""

import logging
from pathlib import Path
from typing import Any

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

from tqdm import tqdm

if TYPE_CHECKING:
    pass


class ProgressTracker:
    """Manages progress bars for file conversion."""

    def __init__(self, total: int = 0, desc: str = "Processing", disable: bool = False):
        """Initialize progress tracker.

        Args:
            total: Total number of items to process
            desc: Description for the progress bar
            disable: If True, disable progress bar
        """
        self.total = total
        self.desc = desc
        self.disable = disable
        self._pbar: Any = None

    def __enter__(self) -> "ProgressTracker":
        """Context manager entry."""
        if not self.disable and self.total > 0:
            self._pbar = tqdm(
                total=self.total,
                desc=self.desc,
                unit="file",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
            )
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        if self._pbar:
            self._pbar.close()

    def update(self, n: int = 1, desc: str | None = None) -> None:
        """Update progress bar.

        Args:
            n: Number of items completed
            desc: Optional new description
        """
        if self._pbar:
            if desc:
                self._pbar.set_description(desc)
            self._pbar.update(n)

    def set_postfix(self, **kwargs: Any) -> None:
        """Set postfix information on progress bar.

        Args:
            **kwargs: Key-value pairs to display as postfix
        """
        if self._pbar:
            self._pbar.set_postfix(**kwargs)


def create_file_progress(path: Path, total_size: int | None = None, disable: bool = False) -> Any:
    """Create a progress bar for individual file encoding.

    Args:
        path: Path to the file being processed
        total_size: Total size in bytes (if known)
        disable: If True, disable progress bar

    Returns:
        tqdm progress bar or None if disabled
    """
    if disable:
        return None

    desc = f"Encoding {path.name}"
    if total_size:
        return tqdm(
            total=total_size,
            desc=desc,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            leave=False,
        )
    # Indeterminate progress
    return tqdm(desc=desc, unit="", leave=False, bar_format="{desc}: {elapsed}")


class TqdmLoggingHandler(logging.Handler):
    """Logging handler that uses tqdm.write to avoid interfering with progress bars."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record.

        Args:
            record: Log record to emit
        """
        try:
            msg = self.format(record)
            tqdm.write(msg)
        except Exception:
            self.handleError(record)
