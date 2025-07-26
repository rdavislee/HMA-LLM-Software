from backend.src.core.config import settings

def test_settings_load():
    assert settings.APP_PORT == 8000
    assert settings.DEFAULT_GRAVITY == -9.81
