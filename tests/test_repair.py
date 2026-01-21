"""Tests for repair module."""

from pathlib import Path
from unittest.mock import patch

from repair import repair_mpeg, repair_wmv, repair_xvid


class TestRepairMpeg:
    """Tests for repair_mpeg function."""

    def test_repair_mpeg(self):
        """Test MPEG-1 repair."""
        input_path = Path("/test/video.mpg")

        with patch("subprocess.run") as mock_run:
            result = repair_mpeg(input_path)

        assert result.name == "video_fixed.mkv"
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "ffmpeg" in args
        assert "-fflags" in args
        assert "+genpts" in args


class TestRepairWmv:
    """Tests for repair_wmv function."""

    def test_repair_wmv(self):
        """Test WMV repair."""
        input_path = Path("/test/video.wmv")

        with patch("subprocess.run") as mock_run:
            result = repair_wmv(input_path)

        assert result.name == "video_fixed.mkv"
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "ffmpeg" in args
        assert "-err_detect" in args


class TestRepairXvid:
    """Tests for repair_xvid function."""

    def test_repair_xvid(self):
        """Test XviD repair."""
        input_path = Path("/test/video.avi")

        with patch("subprocess.run") as mock_run:
            result = repair_xvid(input_path)

        assert result.name == "video_fixed.avi"
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "ffmpeg" in args
        assert "-bsf:v" in args
        assert "mpeg4_unpack_bframes" in args
