"""Tests for parallel encoding functionality."""

from pathlib import Path
from unittest.mock import MagicMock

from converter.parallel import ParallelEncoder


def test_parallel_encoder_init_default():
    """Test ParallelEncoder initialization with default values."""
    encoder = ParallelEncoder()
    assert encoder.max_workers == 4  # Default from config


def test_parallel_encoder_init_custom_workers():
    """Test ParallelEncoder initialization with custom worker count."""
    encoder = ParallelEncoder(max_workers=8)
    assert encoder.max_workers == 8


def test_parallel_encoder_empty_files():
    """Test processing empty file list."""
    encoder = ParallelEncoder()
    convert_func = MagicMock(return_value=True)

    success, fail = encoder.process_files([], convert_func)

    assert success == 0
    assert fail == 0
    convert_func.assert_not_called()


def test_parallel_encoder_single_file_success():
    """Test processing single file successfully."""
    encoder = ParallelEncoder(max_workers=2)
    test_path = Path("/test/video.avi")
    convert_func = MagicMock(return_value=True)

    success, fail = encoder.process_files([test_path], convert_func)

    assert success == 1
    assert fail == 0
    convert_func.assert_called_once_with(test_path)


def test_parallel_encoder_single_file_failure():
    """Test processing single file with failure."""
    encoder = ParallelEncoder(max_workers=2)
    test_path = Path("/test/video.avi")
    convert_func = MagicMock(return_value=False)

    success, fail = encoder.process_files([test_path], convert_func)

    assert success == 0
    assert fail == 1
    convert_func.assert_called_once_with(test_path)


def test_parallel_encoder_multiple_files_all_success():
    """Test processing multiple files, all successful."""
    encoder = ParallelEncoder(max_workers=2)
    test_paths = [Path(f"/test/video{i}.avi") for i in range(5)]
    convert_func = MagicMock(return_value=True)

    success, fail = encoder.process_files(test_paths, convert_func)

    assert success == 5
    assert fail == 0
    assert convert_func.call_count == 5


def test_parallel_encoder_multiple_files_mixed_results():
    """Test processing multiple files with mixed success/failure."""
    encoder = ParallelEncoder(max_workers=2)
    test_paths = [Path(f"/test/video{i}.avi") for i in range(4)]

    # Return True for even indices, False for odd
    def convert_func(path: Path) -> bool:
        idx = int(path.stem[-1])
        return idx % 2 == 0

    success, fail = encoder.process_files(test_paths, convert_func)

    assert success == 2  # videos 0 and 2
    assert fail == 2  # videos 1 and 3


def test_parallel_encoder_with_callback():
    """Test processing with callback function."""
    encoder = ParallelEncoder(max_workers=2)
    test_paths = [Path(f"/test/video{i}.avi") for i in range(3)]
    convert_func = MagicMock(return_value=True)
    callback = MagicMock()

    success, fail = encoder.process_files(test_paths, convert_func, callback)

    assert success == 3
    assert fail == 0
    assert callback.call_count == 3

    # Verify callback was called with correct arguments
    for path in test_paths:
        callback.assert_any_call(path, True)


def test_parallel_encoder_exception_handling():
    """Test handling of exceptions during conversion."""
    encoder = ParallelEncoder(max_workers=2)
    test_paths = [Path(f"/test/video{i}.avi") for i in range(3)]

    def convert_func(path: Path) -> bool:
        idx = int(path.stem[-1])
        if idx == 1:
            raise RuntimeError("Conversion failed")
        return True

    callback = MagicMock()
    success, fail = encoder.process_files(test_paths, convert_func, callback)

    # video0 and video2 succeed, video1 raises exception
    assert success == 2
    assert fail == 1

    # Verify callback was called for all files
    assert callback.call_count == 3


def test_parallel_encoder_worker_count():
    """Test that worker count is respected."""
    # Simply test that different worker counts are accepted
    encoder1 = ParallelEncoder(max_workers=2)
    assert encoder1.max_workers == 2

    encoder2 = ParallelEncoder(max_workers=8)
    assert encoder2.max_workers == 8

    encoder3 = ParallelEncoder(max_workers=1)
    assert encoder3.max_workers == 1
