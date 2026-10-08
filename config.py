from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    bot_token: str
    gemini_api_key: str
    gemini_model: str = "gemini-3.8-flash"
    gemini_model_fallback: str = "gemini-flash-lite-latest"
    db_path: str = "/data/bot.db"
    log_level: str = "INFO"
    tz: str = "Asia/Tashkent"
    bot_language: str = "uz"
    daily_limit_per_user: int = 5
    max_file_size_mb: int = 20
    debug: bool = False
    default_question_count: int = 10
    max_question_count: int = 15

    @classmethod
    def load(cls) -> "Settings":
        token = os.getenv("BOT_TOKEN", "").strip()
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not token:
            raise RuntimeError("BOT_TOKEN is missing. Add it to .env or environment variables.")
        if not gemini_key:
            raise RuntimeError("GEMINI_API_KEY is missing. Add it to .env or environment variables.")

        db_path = os.getenv("DB_PATH", "/data/bot.db").strip() or "/data/bot.db"
        log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper() or "INFO"
        tz_name = os.getenv("TZ", "Asia/Tashkent").strip() or "Asia/Tashkent"

        return cls(
            bot_token=token,
            gemini_api_key=gemini_key,
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip() or "gemini-3.8-flash",
            gemini_model_fallback=os.getenv("GEMINI_MODEL_FALLBACK", "gemini-flash-lite-latest").strip() or "gemini-flash-lite-latest",
            db_path=db_path,
            log_level=log_level,
            tz=tz_name,
            bot_language=os.getenv("BOT_LANGUAGE", "uz").strip() or "uz",
            daily_limit_per_user=int(os.getenv("DAILY_LIMIT_PER_USER", "5")),
            max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", "20")),
            debug=os.getenv("DEBUG", "false").lower() in {"1", "true", "yes"},
            default_question_count=int(os.getenv("DEFAULT_QUESTION_COUNT", "10")),
            max_question_count=int(os.getenv("MAX_QUESTION_COUNT", "15")),
        )


settings = Settings.load()
