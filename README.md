# SportIQ — NBA Narrative Brief

Personal research brief generator for NBA games: fetch box scores + discussion, then use an LLM to produce a short, cited narrative report (themes, claims, narrative vs stats).

## Approach

Deterministic fetch/cache → LLM analysis → report dashboard. Fetch and save are tools (MCP later); analysis stays in the model step. Fixed pipeline first: fetch → filter → analyze → render.

