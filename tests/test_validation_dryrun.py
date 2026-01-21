"""Tests for input validation and dry-run functionality."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from converter.cli import validate_path


class TestValidatePath:
    """Tests for path validation."""

    def test_valid_file(self, tmp_path):
        """Test validation of valid file."""
        test_file = tmp_path / "test.avi"
        test_file.write_text("dummy")

        error = validate_path(test_file)
        assert error is None

    def test_nonexistent_path(self):
        """Test validation of nonexistent path."""
        error = validate_path(Path("/nonexistent/path"))
        assert error is not None
        assert "does not exist" in error

    def test_valid_directory(self, tmp_path):
        """Test validation of valid directory."""
        error = validate_path(tmp_path)
        assert error is None

    def test_unsupported_file_type(self, tmp_path):
        """Test validation of unsupported file type."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("dummy")

        error = validate_path(test_file)
        assert error is not None
        assert "Unsupported file type" in error

    def test_supported_extensions(self, tmp_path):
        """Test all supported extensions."""
        extensions = [".avi", ".mpg", ".mpeg", ".wmv", ".mov"]

        for ext in extensions:
            test_file = tmp_path / f"test{ext}"
            test_file.write_text("dummy")
            error = validate_path(test_file)
            assert error is None, f"Extension {ext} should be supported"


class TestDryRunMode:
    """Tests for dry-run mode."""

    @patch("converter.cli.probe")
    @patch("converter.cli.encode")
    @patch("converter.cli.repair_mpeg")
    @patch("converter.cli.smart_scale")
    def test_dry_run_no_encoding(self, mock_scale, mock_repair, mock_encode, mock_probe, tmp_path):
        """Test that dry-run doesn't actually encode."""
        from converter.cli import convert_file

        # Mock probe to return valid data with all required fields
        mock_probe.return_value = {
            "streams": [{"codec_type": "video", "codec_name": "mpeg1video", "height": 480}],
            "format": {},
        }

        # Mock smart_scale
        mock_scale.return_value = 1.0

        # Mock repair to return a path
        mock_repair.return_value = tmp_path / "fixed.mkv"

        test_file = tmp_path / "test.mpg"
        test_file.write_text("dummy")

        result = convert_file(test_file, dry_run=True)

        # probe should be called with dry_run=True
        assert mock_probe.called
        # encode should be called with dry_run=True
        assert mock_encode.called

    @patch("subprocess.run")
    def test_dry_run_no_subprocess(self, mock_run):
        """Test that dry-run doesn't execute subprocesses."""
        from converter.logging_utils import run_subprocess

        result = run_subprocess(["echo", "test"], dry_run=True)

        mock_run.assert_not_called()
        assert result.success is True
