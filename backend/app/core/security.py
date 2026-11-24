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
    subject: Union[str, Any], role: str = "FREE", expires_delta: Optional[timedelta] = None,
) -> str:
    """Creates a signed JWT access token."""
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode: Dict[str, Any] = {"sub": str(subject), "role": role, "exp": expire, "iat": now, "type": "access"}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Creates a random refresh token."""
    return generate_secure_token(48)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a JWT token."""
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


def create_signup_ticket(email: str, name: str) -> str:
    """Creates a short-lived 10-minute JWT ticket for Google signup."""
    now = datetime.now(timezone.utc)
    to_encode: Dict[str, Any] = {
        "purpose": "google_signup", "email": email.lower().strip(), "name": name,
        "exp": now + timedelta(minutes=10), "iat": now,
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_signup_ticket(ticket: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a Google signup ticket."""
    try:
        payload = jwt.decode(ticket, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload if payload.get("purpose") == "google_signup" else None
    except jwt.PyJWTError:
        return None


def create_oauth_state(intent: str = "login") -> str:
    """Creates a short-lived 10-minute signed JWT for stateless OAuth state."""
    payload = {"intent": intent, "nonce": secrets.token_urlsafe(8), "exp": datetime.now(timezone.utc) + timedelta(minutes=10)}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_oauth_state(state: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a stateless OAuth state JWT."""
    if not state:
        return None
    try:
        payload = jwt.decode(state, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload if isinstance(payload, dict) and "intent" in payload else None
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

