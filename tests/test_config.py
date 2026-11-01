from app.core.config import settings


def test_database_url_is_loaded():
    assert settings.DATABASE_URL.startswith("postgresql+psycopg://")