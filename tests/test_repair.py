"""Tests for repair module."""

from pathlib import Path
from unittest.mock import Mock, patch

from converter.repair import repair_mpeg, repair_wmv, repair_xvid


class TestRepairMpeg:
    """Tests for repair_mpeg function."""

    def test_repair_mpeg(self):
        """Test MPEG-1 repair."""
        input_path = Path("/test/video.mpg")

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = repair_mpeg(input_path)

        assert result.name == "video_fixed.mkv"


class TestRepairWmv:
    """Tests for repair_wmv function."""

    def test_repair_wmv(self):
        """Test WMV repair."""
        input_path = Path("/test/video.wmv")

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = repair_wmv(input_path)

        assert result.name == "video_fixed.mkv"


class TestRepairXvid:
    """Tests for repair_xvid function."""

    def test_repair_xvid(self):
        """Test XviD repair."""
        input_path = Path("/test/video.avi")

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = repair_xvid(input_path)

        assert result.name == "video_fixed.avi"
