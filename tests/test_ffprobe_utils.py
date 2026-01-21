"""Tests for ffprobe_utils module."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

from converter.ffprobe_utils import probe


class TestProbe:
    """Tests for probe function."""

    def test_probe_success(self):
        """Test successful probe."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {
                "streams": [
                    {"codec_type": "video", "codec_name": "h264", "width": 1920, "height": 1080}
                ],
                "format": {"filename": "test.mp4"},
            }
        )

        with patch("subprocess.run", return_value=mock_result):
            result = probe(Path("test.mp4"))

        assert result is not None
        assert "streams" in result
        assert "format" in result
        assert result["streams"][0]["codec_name"] == "h264"

    def test_probe_failure(self):
        """Test probe failure."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error"

        with patch("subprocess.run", return_value=mock_result):
            result = probe(Path("nonexistent.mp4"))

        assert result is None

    def test_probe_invalid_json(self):
        """Test probe with invalid JSON output."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "invalid json"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = probe(Path("test.mp4"))
        
        # Should return None due to JSON parse error
        assert result is None
