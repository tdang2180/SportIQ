"""Clean discussion posts before analyze (code only — no LLM)."""


def filter_posts(posts, keywords=None):
    """
    Dedupe by id and drop empty bodies.
    keywords is unused for now (optional stretch later).
    """
    seen = set()
    cleaned = []

    for post in posts:
        pid = post.get("id")
        body = (post.get("body") or "").strip()

        if not pid or not body:
            continue
        if pid in seen:
            continue

        seen.add(pid)
        cleaned.append(post)

    return cleaned
