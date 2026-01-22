"""Conversion summary utilities."""

import shutil
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ConversionResult:
    """Result of a single file conversion."""

    path: Path
    success: bool
    repaired: bool = False
    warning: str | None = None
    error: str | None = None


@dataclass
class ConversionSummary:
    """Summary of all conversions."""

    results: list[ConversionResult] = field(default_factory=list)

    @property
    def successful_count(self) -> int:
        """Count of successful conversions."""
        return sum(1 for r in self.results if r.success)

    @property
    def error_count(self) -> int:
        """Count of failed conversions."""
        return sum(1 for r in self.results if not r.success)

    @property
    def warning_count(self) -> int:
        """Count of conversions with warnings."""
        return sum(1 for r in self.results if r.warning is not None)

    @property
    def repair_count(self) -> int:
        """Count of files that needed repair."""
        return sum(1 for r in self.results if r.repaired)

    def add_result(
        self,
        path: Path,
        success: bool,
        repaired: bool = False,
        warning: str | None = None,
        error: str | None = None,
    ) -> None:
        """Add a conversion result.

        Args:
            path: Path to the file
            success: Whether conversion succeeded
            repaired: Whether file needed repair
            warning: Optional warning message
            error: Optional error message
        """
        self.results.append(
            ConversionResult(
                path=path, success=success, repaired=repaired, warning=warning, error=error
            )
        )

    def format_summary(self, log_dir: Path, orig_dir: Path, tmp_dir: Path) -> str:
        """Format a human-readable summary.

        Args:
            log_dir: Path to logs directory
            orig_dir: Path to originals directory
            tmp_dir: Path to temporary fixed files directory

        Returns:
            Formatted summary string
        """
        lines = []
        lines.append("")
        lines.append("=" * 60)
        lines.append("Conversion Summary")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Successful conversions: {self.successful_count}")
        lines.append(f"Warnings: {self.warning_count}")
        lines.append(f"Errors: {self.error_count}")
        lines.append(f"Repairs completed: {self.repair_count}")
        lines.append("")

        # Get free disk space
        try:
            stat = shutil.disk_usage(Path.cwd())
            free_gb = stat.free / (1024**3)
            lines.append(f"Free disk space: {free_gb:.2f} GB")
        except Exception:
            lines.append("Free disk space: (unavailable)")

        lines.append("")
        lines.append(f"Logs saved in: {log_dir}")
        lines.append(f"Originals moved to: {orig_dir}")
        lines.append(f"Temp fixed files in: {tmp_dir}")
        lines.append("")
        lines.append("All conversions complete.")
        lines.append("=" * 60)
        lines.append("")

        return "\n".join(lines)
