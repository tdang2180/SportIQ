"""Load discussion posts from mock JSON (swap for Reddit / cache later)."""

import json
from pathlib import Path

MOCK_DIR = Path(__file__).resolve().parents[3] / "data" / "mock"
DISCUSSIONS_PATH = MOCK_DIR / "nba_discussions.json"


def _load_all_discussions():
    with DISCUSSIONS_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def fetch_discussion(game_id):
    """Return posts for a game_id (empty list if none)."""
    return list(_load_all_discussions().get(game_id, []))


def get_cached_posts(game_id):
    """
    Read from cache when we have a DB/cache layer.
    For now there is no cache — always returns None.
    """
    return None
