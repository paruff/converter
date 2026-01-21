import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import LOG_DIR


def write_log(path: Path, text: str) -> None:
    """Legacy function for writing simple log files."""
    path.write_text(text, encoding="utf-8")


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Setup structured logging with session and console handlers.

    Args:
        verbose: If True, set console to DEBUG level, otherwise INFO

    Returns:
        The root logger configured for the session
    """
    # Create logs directory
    LOG_DIR.mkdir(exist_ok=True)

    # Create session log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_log = LOG_DIR / f"session_{timestamp}.log"

    # Configure root logger
    root_logger = logging.getLogger("converter")
    root_logger.setLevel(logging.DEBUG)

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_formatter = logging.Formatter("%(message)s")

    # File handler for session log
    file_handler = logging.FileHandler(session_log, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    root_logger.info(f"Session log: {session_log}")

    return root_logger


def get_file_logger(filepath: Path) -> logging.Logger:
    """Create a logger for a specific file being processed.

    Args:
        filepath: Path to the file being processed

    Returns:
        Logger configured to write to both session and per-file logs
    """
    # Create per-file log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_log = LOG_DIR / f"{filepath.stem}_{timestamp}.log"

    # Get a child logger
    logger = logging.getLogger(f"converter.file.{filepath.name}")

    # Add file-specific handler if not already present
    if not any(
        isinstance(h, logging.FileHandler) and h.baseFilename == str(file_log)
        for h in logger.handlers
    ):
        file_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler = logging.FileHandler(file_log, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


class SubprocessResult:
    """Result of a subprocess execution."""

    def __init__(
        self,
        returncode: int,
        stdout: str,
        stderr: str,
        command: list[str],
        exception: Exception | None = None,
    ):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.command = command
        self.exception = exception

    @property
    def success(self) -> bool:
        """Check if subprocess succeeded."""
        return self.returncode == 0 and self.exception is None

    @property
    def command_str(self) -> str:
        """Get command as string."""
        return " ".join(str(c) for c in self.command)


def run_subprocess(
    command: list[str | Path],
    logger: logging.Logger | None = None,
    capture_output: bool = True,
    check: bool = False,
    dry_run: bool = False,
    **kwargs: Any,
) -> SubprocessResult:
    """Safe subprocess wrapper with logging and error handling.

    Args:
        command: Command to execute as list
        logger: Logger to use (defaults to root logger)
        capture_output: If True, capture stdout/stderr
        check: If True, raise exception on non-zero exit
        dry_run: If True, log command but don't execute
        **kwargs: Additional arguments to pass to subprocess.run

    Returns:
        SubprocessResult with execution details

    Raises:
        subprocess.CalledProcessError: If check=True and command fails
    """
    if logger is None:
        logger = logging.getLogger("converter")

    # Convert Path objects to strings
    cmd_list = [str(c) for c in command]
    cmd_str = " ".join(cmd_list)

    if dry_run:
        logger.info(f"[DRY-RUN] Would execute: {cmd_str}")
        return SubprocessResult(returncode=0, stdout="", stderr="", command=cmd_list)

    logger.debug(f"Executing: {cmd_str}")

    try:
        result = subprocess.run(
            cmd_list,
            capture_output=capture_output,
            text=True,
            check=False,  # We handle errors ourselves
            **kwargs,
        )

        stdout = result.stdout if capture_output else ""
        stderr = result.stderr if capture_output else ""

        if result.returncode == 0:
            logger.debug(f"Command succeeded: {cmd_str}")
        else:
            logger.error(f"Command failed with code {result.returncode}: {cmd_str}")
            if stderr:
                logger.error(f"stderr: {stderr}")

        subprocess_result = SubprocessResult(
            returncode=result.returncode, stdout=stdout, stderr=stderr, command=cmd_list
        )

        if check and not subprocess_result.success:
            raise subprocess.CalledProcessError(
                result.returncode, cmd_list, output=stdout, stderr=stderr
            )

        return subprocess_result

    except Exception as e:
        logger.exception(f"Exception running command: {cmd_str}")
        subprocess_result = SubprocessResult(
            returncode=-1, stdout="", stderr=str(e), command=cmd_list, exception=e
        )

        if check:
            raise

        return subprocess_result
