"""Stub analyze: build brief JSON without calling an LLM."""

DISCLAIMER = (
    "Fan-discussion synthesis only — not official news, injury reports, or betting advice."
)


def analyze_brief(stats, posts):
    """
    Pretend-LLM: look at stats + posts with simple rules.
    Returns the same shape Azure analyze will return later.

    Called by the pipeline (step 5): fetch_box_score → filter_posts → analyze_brief.
      stats = box score dict from fetch_box_score(game_id)
      posts = cleaned list from filter_posts(fetch_discussion(game_id))
    """
    # .get(key, default) — use default if the key is missing (safer than stats["key"])
    home = stats.get("home_team", "Home")
    away = stats.get("away_team", "Away")
    home_score = stats.get("home_score", "?")
    away_score = stats.get("away_score", "?")
    box = stats.get("box_score") or {}
    home_tov = (box.get("home") or {}).get("tov")  # tov = turnovers
    away_tov = (box.get("away") or {}).get("tov")

    # sources = the actual posts we cite (Sources tab in the UI)
    sources = []
    for post in posts:
        sources.append(
            {
                "post_id": post.get("id"),
                "author": post.get("author"),
                "url": post.get("url"),
                "created_utc": post.get("created_utc"),
                "excerpt": (post.get("body") or "")[:160],
            }
        )

    # Stub "understanding": keyword hunt instead of an LLM reading the thread
    # "ref" ≈ referee / officiating; "turnover" ≈ giveaways (matches box-score tov)
    ref_posts = [p for p in posts if "ref" in (p.get("body") or "").lower()]
    tov_posts = [p for p in posts if "turnover" in (p.get("body") or "").lower()]

    # themes = recurring topics fans talked about (Fan narrative tab)
    # claims = specific assertions, labeled as discussion/unverified (Rumors/claims tab)
    themes = []
    claims = []

    if ref_posts:
        themes.append(
            {
                "theme": "Officiating complaints",
                "summary": "Several fans focused on missed calls and physical play.",
                "citation_ids": [p["id"] for p in ref_posts[:3]],  # points at sources
            }
        )
        claims.append(
            {
                "claim": "Refs decided the outcome",
                "label": "discussion",
                "citation_ids": [ref_posts[0]["id"]],
            }
        )

    if tov_posts or (home_tov is not None and away_tov is not None):
        themes.append(
            {
                "theme": "Turnover margin",
                "summary": (
                    f"Ball security showed up in discussion and the box score "
                    f"({home} TOV={home_tov}, {away} TOV={away_tov})."
                ),
                "citation_ids": [p["id"] for p in tov_posts[:3]]
                or ([posts[0]["id"]] if posts else []),
            }
        )
        claims.append(
            {
                "claim": "Turnovers mattered more than officiating",
                "label": "discussion",
                "citation_ids": [p["id"] for p in tov_posts[:2]],
            }
        )

    if not themes:
        themes.append(
            {
                "theme": "General reaction",
                "summary": f"Fans debated the {away} @ {home} result.",
                "citation_ids": [p["id"] for p in posts[:2]],
            }
        )

    # Where fan story matches (or fights) the box score — Overview helper
    narrative_vs_stats = {
        "aligned": [
            "Scoring leaders in the box score match players fans named often."
        ],
        "tension": [],
    }
    if ref_posts:
        narrative_vs_stats["tension"].append(
            "Ref-focused takes are common even when turnover gaps are clearer in the numbers."
        )

    overview = (
        f"{away} {away_score} @ {home} {home_score}. "
        f"Stub analysis over {len(posts)} filtered posts. {DISCLAIMER}"
    )

    return {
        "overview": overview,
        "stats": stats,
        "themes": themes,
        "claims": claims,
        "narrative_vs_stats": narrative_vs_stats,
        "sources": sources,
        "disclaimer": DISCLAIMER,
        "analyze_mode": "stub",
    }
