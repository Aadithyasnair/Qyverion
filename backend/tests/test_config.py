from app.core.config import settings


def test_settings_metadata() -> None:
    """
    Validates configuration module loads metadata properties accurately.
    """
    assert settings.PROJECT_NAME == "Qyverion"
    assert settings.API_V1_STR == "/api/v1"
    assert isinstance(settings.BACKEND_CORS_ORIGINS, list)
