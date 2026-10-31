import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Muat file .env jika ada
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

@dataclass
class Settings:
    app_name: str = os.getenv("APP_NAME", "SellFlow Automation")
    app_env: str = os.getenv("APP_ENV", "development")
    secret_key: str = os.getenv("SECRET_KEY", "CHANGE_THIS_SECRET_KEY")
    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "ChangeThisPassword_2026!")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./sellflow.db")
    session_https_only: bool = os.getenv("SESSION_HTTPS_ONLY", "false").lower() == "true"
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "10"))
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    ai_model: str = os.getenv("AI_MODEL", "gemini-2.5-flash")

    @property
    def ai_provider(self) -> str:
        return "gemini" if self.gemini_api_key.strip() else "builtin"

settings = Settings()

if settings.app_env == "production":
    if settings.secret_key == "CHANGE_THIS_SECRET_KEY" or len(settings.secret_key) < 32:
        raise RuntimeError("SECRET_KEY production wajib diganti dengan string acak minimal 32 karakter.")
    if settings.admin_password in ("ChangeMe123!", "ChangeThisPassword_2026!"):
        raise RuntimeError("ADMIN_PASSWORD production wajib diganti.")
    if settings.database_url.startswith("sqlite"):
        raise RuntimeError("Gunakan PostgreSQL untuk deployment production.")
