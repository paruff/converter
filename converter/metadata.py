"""Metadata fetching and embedding for TV show episodes."""

import json
import logging
import re
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path
from typing import TypedDict


class EpisodeInfo(TypedDict):
    """Episode information parsed from filename."""

    show: str
    season: int
    episode: int


def parse_episode_info(filename: str) -> EpisodeInfo | None:
    """Parse TV show, season, and episode information from filename.

    Supports formats like:
    - Show.Name.S01E05.mkv
    - Show.Name.1x05.mkv
    - Show_Name_S01E05.mkv
    - Show Name - S01E05.mkv

    Args:
        filename: The filename to parse

    Returns:
        Dictionary with 'show', 'season', 'episode' keys, or None if not parsable
    """
    # Remove file extension
    name = Path(filename).stem

    # Pattern for S01E05 format (most common)
    pattern1 = re.compile(r"(.+?)[.\s_-]+S(\d{1,2})E(\d{1,2})", re.IGNORECASE)
    match = pattern1.search(name)
    if match:
        show = match.group(1).replace(".", " ").replace("_", " ").strip()
        season = int(match.group(2))
        episode = int(match.group(3))
        return {"show": show, "season": season, "episode": episode}

    # Pattern for 1x05 format
    pattern2 = re.compile(r"(.+?)[.\s_-]+(\d{1,2})x(\d{1,2})", re.IGNORECASE)
    match = pattern2.search(name)
    if match:
        show = match.group(1).replace(".", " ").replace("_", " ").strip()
        season = int(match.group(2))
        episode = int(match.group(3))
        return {"show": show, "season": season, "episode": episode}

    return None


def fetch_tvmaze_metadata(show_name: str, season: int, episode: int) -> dict[str, str] | None:
    """Fetch episode metadata from TVMaze API.

    Args:
        show_name: Name of the TV show
        season: Season number
        episode: Episode number

    Returns:
        Dictionary with 'title', 'summary', 'airdate', 'runtime' keys, or None if not found
    """
    logger = logging.getLogger("converter")

    try:
        # First, search for the show
        show_query = urllib.parse.quote(show_name)
        search_url = f"https://api.tvmaze.com/search/shows?q={show_query}"

        logger.debug(f"Searching TVMaze for show: {show_name}")
        with urllib.request.urlopen(search_url, timeout=10) as response:
            search_results = json.loads(response.read().decode("utf-8"))

        if not search_results:
            logger.warning(f"No TVMaze results found for show: {show_name}")
            return None

        # Use the first result
        show_id = search_results[0]["show"]["id"]
        show_title = search_results[0]["show"]["name"]
        logger.debug(f"Found show: {show_title} (ID: {show_id})")

        # Fetch episode information
        episode_url = f"https://api.tvmaze.com/shows/{show_id}/episodebynumber?season={season}&number={episode}"

        logger.debug(f"Fetching episode S{season:02d}E{episode:02d} metadata")
        with urllib.request.urlopen(episode_url, timeout=10) as response:
            episode_data = json.loads(response.read().decode("utf-8"))

        # Extract relevant metadata
        metadata = {
            "title": episode_data.get("name", ""),
            "summary": episode_data.get("summary", ""),
            "airdate": episode_data.get("airdate", ""),
            "runtime": str(episode_data.get("runtime", "")),
        }

        # Clean HTML tags and entities from summary
        if metadata["summary"]:
            import html

            # Unescape HTML entities first
            clean_text = html.unescape(metadata["summary"])
            # Remove HTML tags
            clean_text = re.sub(r"<[^>]*>", "", clean_text)
            metadata["summary"] = clean_text

        logger.info(f"Fetched metadata: {metadata['title']} (aired: {metadata['airdate']})")
        return metadata

    except urllib.error.HTTPError as e:
        if e.code == 404:
            logger.warning(f"Episode not found on TVMaze: {show_name} S{season:02d}E{episode:02d}")
        else:
            logger.warning(f"TVMaze API error: {e.code} - {e.reason}")
        return None
    except urllib.error.URLError as e:
        logger.warning(f"Network error fetching metadata: {e.reason}")
        return None
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.warning(f"Error parsing TVMaze response: {e}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error fetching metadata: {e}")
        return None


def embed_metadata(mkv_path: Path, metadata: dict[str, str], dry_run: bool = False) -> bool:
    """Embed metadata into an MKV file using mkvpropedit.

    Args:
        mkv_path: Path to the MKV file
        metadata: Dictionary with metadata to embed
        dry_run: If True, skip actual embedding

    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger("converter")

    if not mkv_path.exists():
        logger.error(f"MKV file not found: {mkv_path}")
        return False

    if dry_run:
        logger.info(f"[DRY-RUN] Would embed metadata into {mkv_path.name}")
        logger.info(f"[DRY-RUN] Metadata: {metadata}")
        return True

    try:
        # Build mkvpropedit command as a list (safe from injection)
        # Each argument is passed separately to subprocess, not interpreted by shell
        cmd = ["mkvpropedit", str(mkv_path)]

        # Add title if available
        if metadata.get("title"):
            # Using format string to create the full argument value
            # This is safe because we're not using shell=True in subprocess.run
            title_value = metadata["title"].replace("\n", " ").replace("\r", " ")
            cmd.extend(["--edit", "info", "--set", f"title={title_value}"])

        # Add description/comment if available
        if metadata.get("summary"):
            # Limit summary length and sanitize newlines
            summary = metadata["summary"][:500].replace("\n", " ").replace("\r", " ")
            cmd.extend(["--edit", "info", "--set", f"comment={summary}"])

        # Add date if available (format: YYYY-MM-DD from TVMaze)
        if metadata.get("airdate"):
            # Validate date format to prevent injection
            airdate = metadata["airdate"]
            if re.match(r"^\d{4}-\d{2}-\d{2}$", airdate):
                cmd.extend(["--edit", "info", "--set", f"date={airdate}"])

        logger.debug(f"Running mkvpropedit: {' '.join(cmd)}")

        # Using list argument (not shell=True) prevents command injection
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=30)

        if result.returncode == 0:
            logger.info(f"✓ Metadata embedded into {mkv_path.name}")
            return True
        logger.warning(f"mkvpropedit failed with code {result.returncode}: {result.stderr}")
        return False

    except FileNotFoundError:
        logger.error(
            "mkvpropedit not found. Please install mkvtoolnix (sudo apt-get install mkvtoolnix)"
        )
        return False
    except subprocess.TimeoutExpired:
        logger.error(f"mkvpropedit timed out for {mkv_path.name}")
        return False
    except Exception as e:
        logger.error(f"Error embedding metadata: {e}")
        return False


def fetch_and_embed_metadata(mkv_path: Path, dry_run: bool = False) -> bool:
    """Fetch metadata from filename and embed it into the MKV file.

    This is the main entry point that combines parsing, fetching, and embedding.

    Args:
        mkv_path: Path to the MKV file
        dry_run: If True, skip actual embedding

    Returns:
        True if successful or if metadata not available, False on error
    """
    logger = logging.getLogger("converter")

    # Parse filename
    episode_info = parse_episode_info(mkv_path.name)
    if not episode_info:
        logger.debug(f"Could not parse episode info from filename: {mkv_path.name}")
        return True  # Not an error, just not a TV show episode

    logger.info(
        f"Parsed episode info: {episode_info['show']} S{episode_info['season']:02d}E{episode_info['episode']:02d}"
    )

    # Fetch metadata
    metadata = fetch_tvmaze_metadata(
        episode_info["show"], episode_info["season"], episode_info["episode"]
    )

    if not metadata:
        logger.info("Metadata not available from TVMaze, skipping embedding")
        return True  # Not an error, just no metadata available

    # Embed metadata
    return embed_metadata(mkv_path, metadata, dry_run=dry_run)
