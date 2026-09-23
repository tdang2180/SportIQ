"""Auth helpers: password hashing, JWT, look up current user."""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import select

from config import get_settings
from db.models import User

# bcrypt turns a plain password into a one-way hash we can store safely
_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
# how long a login token stays valid (learning default)
TOKEN_EXPIRE_DAYS = 7


def hash_password(plain):
    """Turn a plain password into a bcrypt hash for the users table."""
    return _pwd.hash(plain)


def verify_password(plain, password_hash):
    """True if plain password matches the stored hash."""
    return _pwd.verify(plain, password_hash)


def create_access_token(user_id):
    """Build a signed JWT that says 'this is user_id' until it expires."""
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token):
    """Return user_id from a JWT, or None if invalid / expired."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            return None
        return int(sub)
    except (JWTError, ValueError, TypeError):
        return None


def get_current_user(session, token):
    """Load the User row for a Bearer token, or None if bad/missing."""
    user_id = decode_access_token(token)
    if user_id is None:
        return None
    return session.exec(select(User).where(User.id == user_id)).first()
