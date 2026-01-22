"""Tests for metadata module."""

import json
import subprocess
from unittest.mock import Mock, patch

from converter.metadata import (
    embed_metadata,
    fetch_and_embed_metadata,
    fetch_tvmaze_metadata,
    parse_episode_info,
)


class TestParseEpisodeInfo:
    """Tests for parse_episode_info function."""

    def test_parse_sxxexx_format_dots(self):
        """Test parsing S01E05 format with dots."""
        result = parse_episode_info("The.Office.S02E10.mkv")
        assert result == {"show": "The Office", "season": 2, "episode": 10}

    def test_parse_sxxexx_format_underscores(self):
        """Test parsing S01E05 format with underscores."""
        result = parse_episode_info("The_Office_S02E10.mkv")
        assert result == {"show": "The Office", "season": 2, "episode": 10}

    def test_parse_sxxexx_format_spaces(self):
        """Test parsing S01E05 format with spaces."""
        result = parse_episode_info("The Office - S02E10.mkv")
        assert result == {"show": "The Office", "season": 2, "episode": 10}

    def test_parse_sxxexx_format_lowercase(self):
        """Test parsing s01e05 format (lowercase)."""
        result = parse_episode_info("the.office.s02e10.mkv")
        assert result == {"show": "the office", "season": 2, "episode": 10}

    def test_parse_sxxexx_format_single_digit_season(self):
        """Test parsing with single digit season."""
        result = parse_episode_info("Show.Name.S1E05.mkv")
        assert result == {"show": "Show Name", "season": 1, "episode": 5}

    def test_parse_sxxexx_format_single_digit_episode(self):
        """Test parsing with single digit episode."""
        result = parse_episode_info("Show.Name.S01E5.mkv")
        assert result == {"show": "Show Name", "season": 1, "episode": 5}

    def test_parse_1x05_format_dots(self):
        """Test parsing 1x05 format with dots."""
        result = parse_episode_info("The.Office.2x10.mkv")
        assert result == {"show": "The Office", "season": 2, "episode": 10}

    def test_parse_1x05_format_spaces(self):
        """Test parsing 1x05 format with spaces."""
        result = parse_episode_info("The Office - 2x10.mkv")
        assert result == {"show": "The Office", "season": 2, "episode": 10}

    def test_parse_complex_show_name(self):
        """Test parsing show with complex name."""
        result = parse_episode_info("Star.Trek.The.Next.Generation.S03E15.mkv")
        assert result == {"show": "Star Trek The Next Generation", "season": 3, "episode": 15}

    def test_parse_no_match(self):
        """Test parsing filename without episode info."""
        result = parse_episode_info("movie_title.mkv")
        assert result is None

    def test_parse_invalid_format(self):
        """Test parsing invalid format."""
        result = parse_episode_info("Some Random File.avi")
        assert result is None

    def test_parse_with_extra_info(self):
        """Test parsing with extra info after episode number."""
        result = parse_episode_info("Show.Name.S01E05.720p.BluRay.mkv")
        assert result == {"show": "Show Name", "season": 1, "episode": 5}


class TestFetchTVMazeMetadata:
    """Tests for fetch_tvmaze_metadata function."""

    @patch("converter.metadata.urllib.request.urlopen")
    def test_fetch_success(self, mock_urlopen):
        """Test successful metadata fetch."""
        # Mock show search response
        search_response = Mock()
        search_response.read.return_value = json.dumps(
            [{"show": {"id": 123, "name": "The Office"}}]
        ).encode("utf-8")
        search_response.__enter__ = Mock(return_value=search_response)
        search_response.__exit__ = Mock(return_value=False)

        # Mock episode response
        episode_response = Mock()
        episode_response.read.return_value = json.dumps(
            {
                "name": "Diversity Day",
                "summary": "<p>Michael's diversity training goes wrong.</p>",
                "airdate": "2005-03-29",
                "runtime": 22,
            }
        ).encode("utf-8")
        episode_response.__enter__ = Mock(return_value=episode_response)
        episode_response.__exit__ = Mock(return_value=False)

        mock_urlopen.side_effect = [search_response, episode_response]

        result = fetch_tvmaze_metadata("The Office", 1, 2)

        assert result == {
            "title": "Diversity Day",
            "summary": "Michael's diversity training goes wrong.",
            "airdate": "2005-03-29",
            "runtime": "22",
        }

    @patch("converter.metadata.urllib.request.urlopen")
    def test_fetch_show_not_found(self, mock_urlopen):
        """Test when show is not found."""
        search_response = Mock()
        search_response.read.return_value = json.dumps([]).encode("utf-8")
        search_response.__enter__ = Mock(return_value=search_response)
        search_response.__exit__ = Mock(return_value=False)

        mock_urlopen.return_value = search_response

        result = fetch_tvmaze_metadata("NonExistentShow", 1, 1)
        assert result is None

    @patch("converter.metadata.urllib.request.urlopen")
    def test_fetch_episode_not_found(self, mock_urlopen):
        """Test when episode is not found (404 error)."""
        # Mock show search response
        search_response = Mock()
        search_response.read.return_value = json.dumps(
            [{"show": {"id": 123, "name": "The Office"}}]
        ).encode("utf-8")
        search_response.__enter__ = Mock(return_value=search_response)
        search_response.__exit__ = Mock(return_value=False)

        # Mock episode 404 error
        import urllib.error

        episode_error = urllib.error.HTTPError("url", 404, "Not Found", {}, None)  # type: ignore

        mock_urlopen.side_effect = [search_response, episode_error]

        result = fetch_tvmaze_metadata("The Office", 1, 99)
        assert result is None

    @patch("converter.metadata.urllib.request.urlopen")
    def test_fetch_network_error(self, mock_urlopen):
        """Test network error during fetch."""
        import urllib.error

        mock_urlopen.side_effect = urllib.error.URLError("Network error")

        result = fetch_tvmaze_metadata("The Office", 1, 1)
        assert result is None

    @patch("converter.metadata.urllib.request.urlopen")
    def test_fetch_invalid_json(self, mock_urlopen):
        """Test invalid JSON response."""
        search_response = Mock()
        search_response.read.return_value = b"invalid json"
        search_response.__enter__ = Mock(return_value=search_response)
        search_response.__exit__ = Mock(return_value=False)

        mock_urlopen.return_value = search_response

        result = fetch_tvmaze_metadata("The Office", 1, 1)
        assert result is None

    @patch("converter.metadata.urllib.request.urlopen")
    def test_fetch_missing_fields(self, mock_urlopen):
        """Test when response has missing fields."""
        # Mock show search response
        search_response = Mock()
        search_response.read.return_value = json.dumps(
            [{"show": {"id": 123, "name": "The Office"}}]
        ).encode("utf-8")
        search_response.__enter__ = Mock(return_value=search_response)
        search_response.__exit__ = Mock(return_value=False)

        # Mock episode response with missing fields
        episode_response = Mock()
        episode_response.read.return_value = json.dumps({"name": "Episode Title"}).encode("utf-8")
        episode_response.__enter__ = Mock(return_value=episode_response)
        episode_response.__exit__ = Mock(return_value=False)

        mock_urlopen.side_effect = [search_response, episode_response]

        result = fetch_tvmaze_metadata("The Office", 1, 1)

        # Should succeed but with empty strings for missing fields
        assert result == {"title": "Episode Title", "summary": "", "airdate": "", "runtime": ""}


class TestEmbedMetadata:
    """Tests for embed_metadata function."""

    @patch("converter.metadata.subprocess.run")
    def test_embed_success(self, mock_run, tmp_path):
        """Test successful metadata embedding."""
        # Create a dummy MKV file
        mkv_file = tmp_path / "test.mkv"
        mkv_file.touch()

        mock_run.return_value = Mock(returncode=0, stderr="")

        metadata = {
            "title": "Episode Title",
            "summary": "Episode summary",
            "airdate": "2020-01-15",
        }

        result = embed_metadata(mkv_file, metadata, dry_run=False)

        assert result is True
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert "mkvpropedit" in call_args
        assert str(mkv_file) in call_args

    @patch("converter.metadata.subprocess.run")
    def test_embed_dry_run(self, mock_run, tmp_path):
        """Test dry run mode for metadata embedding."""
        mkv_file = tmp_path / "test.mkv"
        mkv_file.touch()

        metadata = {"title": "Episode Title"}

        result = embed_metadata(mkv_file, metadata, dry_run=True)

        assert result is True
        assert not mock_run.called  # Should not run mkvpropedit in dry run mode

    def test_embed_file_not_found(self, tmp_path):
        """Test embedding when file doesn't exist."""
        mkv_file = tmp_path / "nonexistent.mkv"

        metadata = {"title": "Episode Title"}

        result = embed_metadata(mkv_file, metadata, dry_run=False)
        assert result is False

    @patch("converter.metadata.subprocess.run")
    def test_embed_mkvpropedit_not_found(self, mock_run, tmp_path):
        """Test when mkvpropedit is not installed."""
        mkv_file = tmp_path / "test.mkv"
        mkv_file.touch()

        mock_run.side_effect = FileNotFoundError()

        metadata = {"title": "Episode Title"}

        result = embed_metadata(mkv_file, metadata, dry_run=False)
        assert result is False

    @patch("converter.metadata.subprocess.run")
    def test_embed_mkvpropedit_failure(self, mock_run, tmp_path):
        """Test when mkvpropedit returns non-zero exit code."""
        mkv_file = tmp_path / "test.mkv"
        mkv_file.touch()

        mock_run.return_value = Mock(returncode=1, stderr="Error message")

        metadata = {"title": "Episode Title"}

        result = embed_metadata(mkv_file, metadata, dry_run=False)
        assert result is False

    @patch("converter.metadata.subprocess.run")
    def test_embed_timeout(self, mock_run, tmp_path):
        """Test timeout during embedding."""
        mkv_file = tmp_path / "test.mkv"
        mkv_file.touch()

        mock_run.side_effect = subprocess.TimeoutExpired("mkvpropedit", 30)

        metadata = {"title": "Episode Title"}

        result = embed_metadata(mkv_file, metadata, dry_run=False)
        assert result is False

    @patch("converter.metadata.subprocess.run")
    def test_embed_with_all_metadata_fields(self, mock_run, tmp_path):
        """Test embedding with all metadata fields."""
        mkv_file = tmp_path / "test.mkv"
        mkv_file.touch()

        mock_run.return_value = Mock(returncode=0, stderr="")

        metadata = {
            "title": "Episode Title",
            "summary": "A" * 600,  # Long summary
            "airdate": "2020-01-15",
            "runtime": "42",
        }

        result = embed_metadata(mkv_file, metadata, dry_run=False)

        assert result is True
        call_args = mock_run.call_args[0][0]
        # Check that summary was truncated to 500 chars
        summary_arg = [arg for arg in call_args if arg.startswith("comment=")]
        assert len(summary_arg[0]) <= 508  # "comment=" prefix + 500 chars


class TestFetchAndEmbedMetadata:
    """Tests for fetch_and_embed_metadata function."""

    @patch("converter.metadata.embed_metadata")
    @patch("converter.metadata.fetch_tvmaze_metadata")
    @patch("converter.metadata.parse_episode_info")
    def test_fetch_and_embed_success(self, mock_parse, mock_fetch, mock_embed, tmp_path):
        """Test successful fetch and embed."""
        mkv_file = tmp_path / "The.Office.S01E02.mkv"
        mkv_file.touch()

        mock_parse.return_value = {"show": "The Office", "season": 1, "episode": 2}
        mock_fetch.return_value = {"title": "Episode Title", "summary": "Summary"}
        mock_embed.return_value = True

        result = fetch_and_embed_metadata(mkv_file, dry_run=False)

        assert result is True
        mock_parse.assert_called_once()
        mock_fetch.assert_called_once_with("The Office", 1, 2)
        mock_embed.assert_called_once()

    @patch("converter.metadata.parse_episode_info")
    def test_fetch_and_embed_no_episode_info(self, mock_parse, tmp_path):
        """Test when filename doesn't contain episode info."""
        mkv_file = tmp_path / "movie.mkv"
        mkv_file.touch()

        mock_parse.return_value = None

        result = fetch_and_embed_metadata(mkv_file, dry_run=False)

        # Should return True (not an error, just not a TV show)
        assert result is True

    @patch("converter.metadata.fetch_tvmaze_metadata")
    @patch("converter.metadata.parse_episode_info")
    def test_fetch_and_embed_metadata_not_found(self, mock_parse, mock_fetch, tmp_path):
        """Test when metadata is not found."""
        mkv_file = tmp_path / "The.Office.S01E02.mkv"
        mkv_file.touch()

        mock_parse.return_value = {"show": "The Office", "season": 1, "episode": 2}
        mock_fetch.return_value = None

        result = fetch_and_embed_metadata(mkv_file, dry_run=False)

        # Should return True (not an error, just no metadata)
        assert result is True

    @patch("converter.metadata.embed_metadata")
    @patch("converter.metadata.fetch_tvmaze_metadata")
    @patch("converter.metadata.parse_episode_info")
    def test_fetch_and_embed_embedding_failure(self, mock_parse, mock_fetch, mock_embed, tmp_path):
        """Test when embedding fails."""
        mkv_file = tmp_path / "The.Office.S01E02.mkv"
        mkv_file.touch()

        mock_parse.return_value = {"show": "The Office", "season": 1, "episode": 2}
        mock_fetch.return_value = {"title": "Episode Title"}
        mock_embed.return_value = False

        result = fetch_and_embed_metadata(mkv_file, dry_run=False)

        # Should return False when embedding fails
        assert result is False
