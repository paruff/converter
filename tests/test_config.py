"""Tests for config module."""

from pathlib import Path

from converter.config import DEFAULT_SD_BITRATE, LOG_DIR, ORIG_DIR, ROOT, TMP_DIR


class TestConfig:
    """Tests for config module."""

    def test_root_is_path(self):
        """Test ROOT is a Path object."""
        assert isinstance(ROOT, Path)

    def test_log_dir_is_path(self):
        """Test LOG_DIR is a Path object."""
        assert isinstance(LOG_DIR, Path)

    def test_tmp_dir_is_path(self):
        """Test TMP_DIR is a Path object."""
        assert isinstance(TMP_DIR, Path)

    def test_orig_dir_is_path(self):
        """Test ORIG_DIR is a Path object."""
        assert isinstance(ORIG_DIR, Path)

    def test_default_bitrate(self):
        """Test default SD bitrate value."""
        assert DEFAULT_SD_BITRATE == 1_200_000
        assert isinstance(DEFAULT_SD_BITRATE, int)
