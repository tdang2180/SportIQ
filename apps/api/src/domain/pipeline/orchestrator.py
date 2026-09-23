"""Fixed checklist: fetch → filter → analyze → (optional) persist draft."""

from domain.analyze import analyze_brief
from domain.fetch import fetch_box_score, fetch_discussion
from domain.filter import filter_posts
from db.models import Brief, PipelineLog


def run_pipeline(game_id, user=None, session=None):
    """
    Run the brief workflow for one game.
    If user + session are passed, also insert a draft Brief + PipelineLog row.
    """
    # 1. Stats from mock/API
    stats = fetch_box_score(game_id)

    # 2. Discussion posts, then clean them in code
    posts = filter_posts(fetch_discussion(game_id))

    # 3. Stub (or later Azure) → structured brief JSON
    content = analyze_brief(stats, posts)

    # 4. Persist draft for this user (step 6) — skip if no DB/user yet
    if user is not None and session is not None:
        save_brief(
            session,
            user,
            content,
            steps=["fetch_box_score", "fetch_discussion", "filter_posts", "analyze_brief"],
        )

    return content


def save_brief(session, user, content, status="draft", steps=None):
    """
    Insert a Brief row owned by user (plus a PipelineLog audit row).
    content = the dict from analyze_brief(); game fields come from content["stats"].
    status: "draft" after analyze, "saved" after the user confirms (routes later).
    """
    stats = content.get("stats") or {}
    game_id = stats.get("game_id") or ""

    row = Brief(
        user_id=user.id,
        game_id=game_id,
        home_team=stats.get("home_team") or "",
        away_team=stats.get("away_team") or "",
        game_date=stats.get("game_date") or "",
        status=status,
        content=content,
    )
    session.add(row)
    session.commit()
    session.refresh(row)  # fill in row.id from Postgres

    log = PipelineLog(
        user_id=user.id,
        brief_id=row.id,
        game_id=game_id,
        steps=steps or [],
        tool_calls=[],
    )
    session.add(log)
    session.commit()

    return row
