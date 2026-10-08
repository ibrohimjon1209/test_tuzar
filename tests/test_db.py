import importlib


def test_db_initializes_sqlite(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "data" / "bot.db"))

    import db
    importlib.reload(db)
    db.init_db()

    assert db.DB_PATH.exists()
    assert db.DB_PATH.parent.exists()
