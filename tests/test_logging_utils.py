"""Tests for logging_utils module."""

from logging_utils import write_log


class TestWriteLog:
    """Tests for write_log function."""

    def test_write_log(self, tmp_path):
        """Test writing log to file."""
        log_file = tmp_path / "test.log"
        text = "Test log message"

        write_log(log_file, text)

        assert log_file.exists()
        assert log_file.read_text(encoding="utf-8") == text

    def test_write_log_overwrite(self, tmp_path):
        """Test overwriting existing log file."""
        log_file = tmp_path / "test.log"

        write_log(log_file, "First message")
        write_log(log_file, "Second message")

        assert log_file.read_text(encoding="utf-8") == "Second message"

    def test_write_log_unicode(self, tmp_path):
        """Test writing log with unicode characters."""
        log_file = tmp_path / "test.log"
        text = "Test with unicode: 日本語 🎬"

        write_log(log_file, text)

        assert log_file.read_text(encoding="utf-8") == text
