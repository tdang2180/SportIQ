"""Fixed checklist: fetch → filter → analyze (persist comes in DB step)."""

from domain.analyze import analyze_brief
from domain.fetch import fetch_box_score, fetch_discussion
from domain.filter import filter_posts


def run_pipeline(game_id):
    """
    Run the brief workflow for one game.
    Routes / MCP will call this later instead of wiring steps themselves.
    """
    # 1. Stats from mock/API
    stats = fetch_box_score(game_id)

    # 2. Discussion posts, then clean them in code
    posts = filter_posts(fetch_discussion(game_id))

    # 3. Stub (or later Azure) → structured brief JSON
    brief = analyze_brief(stats, posts)

    return brief


# save_brief(user, brief) — step 6 once we have a DB
