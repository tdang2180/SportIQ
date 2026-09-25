"""POST /auth/signup, /auth/login, /auth/logout."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from auth import create_access_token, hash_password, verify_password
from db.models import User, get_session
from schemas import LoginRequest, SignupRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def get_db():
    """FastAPI dependency: one DB session per request, then close it."""
    session = get_session()
    try:
        yield session
    finally:
        session.close()


@router.post("/signup", response_model=TokenResponse)
def signup(body: SignupRequest, session=Depends(get_db)):
    """Create a user and return a JWT (so they're logged in immediately)."""
    existing = session.exec(select(User).where(User.email == body.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return TokenResponse(
        access_token=create_access_token(user.id),
        user_id=user.id,
        email=user.email,
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, session=Depends(get_db)):
    """Check email/password and return a JWT."""
    user = session.exec(select(User).where(User.email == body.email)).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return TokenResponse(
        access_token=create_access_token(user.id),
        user_id=user.id,
        email=user.email,
    )


@router.post("/logout")
def logout():
    """JWT is stateless — tell the client to drop the token."""
    return {"ok": True, "detail": "Delete the access_token on the client"}
