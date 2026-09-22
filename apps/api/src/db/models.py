"""SQLModel tables = Python classes that map to Postgres tables."""

from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime
from sqlmodel import Field, Session, SQLModel, create_engine

from config import get_settings


def utcnow():
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    """Someone who can sign up and own briefs."""

    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=320)
    password_hash: str  # never store plain passwords
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True)),
    )


class Brief(SQLModel, table=True):
    """One narrative brief for a game, owned by a user."""

    __tablename__ = "briefs"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    game_id: str = Field(index=True, max_length=64)
    home_team: str = Field(max_length=64)
    away_team: str = Field(max_length=64)
    game_date: str = Field(max_length=32)
    # draft = just analyzed; saved = user confirmed keep
    status: str = Field(default="draft", max_length=32)
    # full analyze_brief() JSON (themes, claims, sources, …)
    content: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True)),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True)),
    )


class Run(SQLModel, table=True):
    """Audit log for one pipeline run (good for interviews / debugging)."""

    __tablename__ = "runs"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    brief_id: int | None = Field(default=None, foreign_key="briefs.id", index=True)
    game_id: str = Field(max_length=64)
    steps: list = Field(default_factory=list, sa_column=Column(JSON))
    tool_calls: list = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True)),
    )


class CacheEntry(SQLModel, table=True):
    """Optional cache for fetched game/discussion payloads (later)."""

    __tablename__ = "cache_entries"

    id: int | None = Field(default=None, primary_key=True)
    cache_key: str = Field(index=True, unique=True, max_length=256)
    kind: str = Field(max_length=64)  # "game" | "discussion"
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True)),
    )


# --- engine / sessions (substep B: needed to create tables) ---

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        url = get_settings().database_url
        _engine = create_engine(url, echo=False)
    return _engine


def init_db():
    """
    Dev helper: create missing tables quickly.
    Prefer Alembic for real schema changes:
      poetry run alembic revision --autogenerate -m "message"
      poetry run alembic upgrade head
    """
    SQLModel.metadata.create_all(get_engine())


def get_session():
    """Open a DB session (use in a with-block or FastAPI Depends later)."""
    return Session(get_engine())
