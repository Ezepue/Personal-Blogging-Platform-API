"""Application configuration.

All environment-derived settings live on a single ``Settings`` object so the
rest of the codebase depends on one well-defined surface (SRP) instead of
scattered ``os.getenv`` calls. Module-level aliases are exported for concise
imports at call sites.
"""
import os
import warnings

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")


class Settings:
    """Validated runtime configuration, loaded once at import."""

    def __init__(self) -> None:
        self.DATABASE_URL: str = self._require("DATABASE_URL")
        self.SECRET_KEY: str = self._require("SECRET_KEY")
        self.ALGORITHM: str = "HS256"

        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = self._bounded_int(
            "ACCESS_TOKEN_EXPIRE_MINUTES", default=30, lo=1, hi=1440
        )
        self.REFRESH_TOKEN_EXPIRE_DAYS: int = self._bounded_int(
            "REFRESH_TOKEN_EXPIRE_DAYS", default=7, lo=1, hi=365
        )

        self.UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", os.path.abspath("uploads"))
        self.FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
        self.ALLOWED_HOSTS: list[str] = [
            h.strip() for h in os.getenv("ALLOWED_HOSTS", "*").split(",") if h.strip()
        ]

        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)

        if len(self.SECRET_KEY) < 32:
            warnings.warn(
                "SECRET_KEY is shorter than 32 characters. Use a strong random key in production.",
                stacklevel=2,
            )

    @staticmethod
    def _require(name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise ValueError(f"{name} is required. Set it in the environment or .env file.")
        return value

    @staticmethod
    def _bounded_int(name: str, default: int, lo: int, hi: int) -> int:
        value = int(os.getenv(name, default))
        if not (lo <= value <= hi):
            raise ValueError(f"{name} must be between {lo} and {hi}.")
        return value


settings = Settings()

DATABASE_URL = settings.DATABASE_URL
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
UPLOAD_FOLDER = settings.UPLOAD_FOLDER
FRONTEND_URL = settings.FRONTEND_URL
ALLOWED_HOSTS = settings.ALLOWED_HOSTS
