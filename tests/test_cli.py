"""Integration tests for CLI module."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from converter.cli import main


class TestCLIIntegration:
    """Integration tests for CLI."""

    def test_cli_help(self):
        """Test CLI help message."""
        with patch.object(sys, "argv", ["cli.py", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_cli_version(self):
        """Test CLI version."""
        with patch.object(sys, "argv", ["cli.py", "--version"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_cli_invalid_path(self):
        """Test CLI with invalid path."""
        with patch.object(sys, "argv", ["cli.py", "/nonexistent/path"]):
            result = main()
            assert result == 1

    @patch("converter.cli.convert_file")
    def test_cli_single_file(self, mock_convert):
        """Test CLI with single file."""
        # Mock convert_file to return success
        mock_convert.return_value = True

        # Create a temp file for testing
        with patch("converter.cli.Path") as mock_path_class:
            mock_file = Mock()
            mock_file.exists.return_value = True
            mock_file.is_file.return_value = True
            mock_file.is_dir.return_value = False
            mock_file.suffix = ".avi"
            mock_file.stat.return_value = Mock()
            mock_path_class.return_value = mock_file
            
            with patch.object(sys, "argv", ["cli.py", "test.avi"]):
                result = main()

            assert result == 0
            mock_convert.assert_called_once()

    @patch("converter.cli.convert_directory")
    def test_cli_directory(self, mock_convert_dir):
        """Test CLI with directory."""
        # Mock convert_directory to return success
        mock_convert_dir.return_value = (5, 0)  # 5 success, 0 failures

        with patch("converter.cli.Path") as mock_path_class:
            mock_dir = Mock()
            mock_dir.exists.return_value = True
            mock_dir.is_file.return_value = False
            mock_dir.is_dir.return_value = True
            mock_dir.iterdir.return_value = [Mock(is_file=lambda: True, suffix=".avi")]
            mock_path_class.return_value = mock_dir
            
            with patch.object(sys, "argv", ["cli.py", "/test/dir"]):
                result = main()

            assert result == 0
            mock_convert_dir.assert_called_once()
