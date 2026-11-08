import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
import bcrypt
import jwt
from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a bcrypt hash."""
    try:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Generates a bcrypt hash for the provided password."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def hash_token(token: str) -> str:
    """Hashes a token with SHA-256 for secure storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_secure_token(nbytes: int = 32) -> str:
    """Generates a cryptographically strong URL-safe random string."""
    return secrets.token_urlsafe(nbytes)


def create_access_token(
    subject: Union[str, Any],
    role: str = "FREE",
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Creates a signed JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Creates a random refresh token."""
    return generate_secure_token(48)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.PyJWTError:
        return None


def create_signup_ticket(email: str, name: str) -> str:
    """Creates a short-lived 10-minute JWT ticket for Google signup."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=10)
    to_encode: Dict[str, Any] = {
        "purpose": "google_signup",
        "email": email.lower().strip(),
        "name": name,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_signup_ticket(ticket: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a Google signup ticket."""
    try:
        payload = jwt.decode(
            ticket,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("purpose") != "google_signup":
            return None
        return payload
    except jwt.PyJWTError:
        return None


def sanitize_csv_formula(val: Any) -> str:
    """
    Sanitizes values against CSV Formula Injection (CWE-1236 / OWASP).
    If a string begins with '=', '+', '-', '@', '\t', or '\r' (even after leading spaces),
    it prepends a single quote "'" to neutralize formula execution in spreadsheet software.
    """
    if val is None:
        return ""
    s = str(val)
    if not s:
        return ""
    if s[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + s
    stripped = s.lstrip(" ")
    if stripped and stripped[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + s
    return s

