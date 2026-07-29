"""Shared FastAPI dependencies (auth, DB session)."""
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

# tokenUrl points at our login endpoint so /docs "Authorize" works.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the current user from a JWT bearer token."""
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    subject = decode_access_token(token)
    if subject is None:
        raise credentials_exc
    try:
        user_id = uuid.UUID(subject)
    except (ValueError, TypeError) as exc:  # noqa: F841
        raise credentials_exc from None

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_exc
    return user
