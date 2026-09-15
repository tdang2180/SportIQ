"""Load game / box score data from mock JSON (swap for live API later)."""

import json
from pathlib import Path

# apps/api/src/domain/fetch/game.py → parents[3] == apps/api
MOCK_DIR = Path(__file__).resolve().parents[3] / "data" / "mock"
GAMES_PATH = MOCK_DIR / "nba_games.json"


def _load_games():
    with GAMES_PATH.open(encoding="utf-8") as f:
        return json.load(f)["games"]


def list_games():
    """Return a light list of games (no full box score)."""
    return [
        {
            "game_id": g["game_id"],
            "home_team": g["home_team"],
            "away_team": g["away_team"],
            "game_date": g["game_date"],
            "home_score": g["home_score"],
            "away_score": g["away_score"],
        }
        for g in _load_games()
    ]


def fetch_game(game_id):
    """Return the full game record, including box_score."""
    for game in _load_games():
        if game["game_id"] == game_id:
            return game
    raise KeyError(f"Unknown game_id: {game_id}")


def fetch_box_score(game_id):
    """Return stats-focused view of a game (what analyze will use)."""
    game = fetch_game(game_id)
    return {
        "game_id": game["game_id"],
        "home_team": game["home_team"],
        "away_team": game["away_team"],
        "game_date": game["game_date"],
        "home_score": game["home_score"],
        "away_score": game["away_score"],
        "box_score": game["box_score"],
    }
