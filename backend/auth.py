import time
from collections import defaultdict
from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from backend.config import settings
from backend.models import User

password_hash_engine = PasswordHash.recommended()

# In-memory rate limiting for login attempts
# key: client_ip / identifier -> list of failed attempt timestamps
_failed_attempts: dict[str, list[float]] = defaultdict(list)
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 300  # 5 minutes

def hash_password(plain_password: str) -> str:
    return password_hash_engine.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash_engine.verify(plain_password, hashed_password)

def check_login_rate_limit(client_id: str) -> None:
    now = time.time()
    # Retain only attempts within window
    _failed_attempts[client_id] = [t for t in _failed_attempts[client_id] if now - t < LOCKOUT_SECONDS]
    if len(_failed_attempts[client_id]) >= MAX_FAILED_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Terlalu banyak percobaan login yang gagal. Coba lagi dalam beberapa menit."
        )

def record_login_failure(client_id: str) -> None:
    _failed_attempts[client_id].append(time.time())

def clear_login_failures(client_id: str) -> None:
    if client_id in _failed_attempts:
        del _failed_attempts[client_id]

def ensure_initial_admin(db: Session) -> User:
    """Pastikan setidaknya ada satu akun admin di database."""
    user = db.query(User).filter(User.username == settings.admin_username).first()
    if not user:
        user = User(
            username=settings.admin_username,
            password_hash=hash_password(settings.admin_password),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username, User.is_active == True).first()
    if not user:
        # Jika belum ada user di database, cek apakah cocok dengan bootstrap admin
        if db.query(User).count() == 0 and username == settings.admin_username:
            user = ensure_initial_admin(db)
        else:
            return None

    if not verify_password(password, user.password_hash):
        return None
    return user

def require_login(request: Request) -> None:
    if not request.session.get("authenticated"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Silakan login terlebih dahulu."
        )
