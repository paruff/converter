"""Parallel encoding using ThreadPoolExecutor for concurrent video conversion."""

import logging
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable

from .config import MAX_WORKERS
from .progress import ProgressTracker


class ParallelEncoder:
    """Manages parallel video encoding using thread pool."""

    def __init__(
        self,
        max_workers: int | None = None,
        logger: logging.Logger | None = None,
        show_progress: bool = True,
    ):
        """Initialize parallel encoder.

        Args:
            max_workers: Maximum number of worker threads (default: from config)
            logger: Logger instance
            show_progress: If True, show progress bar
        """
        self.max_workers = max_workers or MAX_WORKERS
        self.logger = logger or logging.getLogger("converter")
        self.show_progress = show_progress

    def process_files(
        self,
        files: list[Path],
        convert_func: Callable[[Path], bool],
        callback: Callable[[Path, bool], None] | None = None,
    ) -> tuple[int, int]:
        """Process multiple files in parallel.

        Args:
            files: List of file paths to process
            convert_func: Function to convert a single file (returns success status)
            callback: Optional callback function called after each file (path, success)

        Returns:
            Tuple of (successful_count, failed_count)
        """
        if not files:
            self.logger.warning("No files to process")
            return 0, 0

        success_count = 0
        fail_count = 0

        self.logger.info(
            f"Starting parallel encoding with {self.max_workers} worker(s) for {len(files)} file(s)"
        )

        with ProgressTracker(
            total=len(files), desc="Converting files", disable=not self.show_progress
        ) as progress:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all jobs
                future_to_path: dict[Future[bool], Path] = {
                    executor.submit(convert_func, path): path for path in files
                }

                # Process completed jobs
                for future in as_completed(future_to_path):
                    path = future_to_path[future]
                    try:
                        success = future.result()
                        if success:
                            success_count += 1
                        else:
                            fail_count += 1

                        # Update progress bar
                        progress.update(1)
                        progress.set_postfix(success=success_count, failed=fail_count)

                        # Call callback if provided
                        if callback:
                            callback(path, success)

                    except Exception as e:
                        self.logger.exception(f"Error processing {path.name}: {e}")
                        fail_count += 1
                        progress.update(1)
                        progress.set_postfix(success=success_count, failed=fail_count)
                        if callback:
                            callback(path, False)

        self.logger.info(
            f"Parallel encoding complete: {success_count} succeeded, {fail_count} failed"
        )
        return success_count, fail_count
