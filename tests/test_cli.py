"""Integration tests for CLI module."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from converter.cli import convert_file, main


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


class TestNoInplaceOverwrite:
    """Test that convert_file avoids in-place overwrites."""

    @patch("converter.cli.encode")
    @patch("converter.cli.probe")
    @patch("converter.cli.get_file_logger")
    def test_no_inplace_overwrite_mkv(self, mock_logger, mock_probe, mock_encode):
        """Test that .mkv input produces _converted.mkv output."""
        # Setup mocks
        mock_probe.return_value = {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "bit_rate": "2000000",
                    "height": 720,
                }
            ]
        }
        mock_logger.return_value = Mock()

        # Create a mock .mkv file path
        input_path = Path("/test/video.mkv")

        with patch.object(Path, "exists", return_value=True):
            with patch.object(Path, "is_file", return_value=True):
                with patch.object(Path, "stat", return_value=Mock()):
                    convert_file(input_path, dry_run=True)

        # Verify encode was called with different paths
        mock_encode.assert_called_once()
        args = mock_encode.call_args[0]
        input_arg = args[0]
        output_arg = args[1]

        # Output should be video_converted.mkv, not video.mkv
        assert output_arg.name == "video_converted.mkv"
        assert output_arg != input_path

    @patch("converter.cli.encode")
    @patch("converter.cli.probe")
    @patch("converter.cli.get_file_logger")
    def test_no_inplace_overwrite_avi(self, mock_logger, mock_probe, mock_encode):
        """Test that .avi input produces .mkv output (different files)."""
        # Setup mocks
        mock_probe.return_value = {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "bit_rate": "2000000",
                    "height": 720,
                }
            ]
        }
        mock_logger.return_value = Mock()

        # Create a mock .avi file path
        input_path = Path("/test/video.avi")

        with patch.object(Path, "exists", return_value=True):
            with patch.object(Path, "is_file", return_value=True):
                with patch.object(Path, "stat", return_value=Mock()):
                    convert_file(input_path, dry_run=True)

        # Verify encode was called with different paths
        mock_encode.assert_called_once()
        args = mock_encode.call_args[0]
        input_arg = args[0]
        output_arg = args[1]

        # Output should be video.mkv, different from video.avi
        assert output_arg.name == "video.mkv"
        assert output_arg != input_path
