import importlib

import config


def test_settings_reads_env(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "test-token")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.8-flash")
    monkeypatch.setenv("GEMINI_MODEL_FALLBACK", "gemini-flash-lite-latest")
    monkeypatch.setenv("DB_PATH", "/tmp/test_bot/bot.db")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("TZ", "Asia/Tashkent")

    importlib.reload(config)
    settings = config.Settings.load()

    assert settings.bot_token == "test-token"
    assert settings.gemini_api_key == "test-gemini-key"
    assert settings.db_path == "/tmp/test_bot/bot.db"
    assert settings.log_level == "DEBUG"
    assert settings.tz == "Asia/Tashkent"
