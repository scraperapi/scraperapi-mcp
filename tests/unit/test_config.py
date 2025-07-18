import pytest


class TestConfig:
    @pytest.fixture
    def mock_settings(self, mocker):
        return mocker.patch("scraperapi_mcp_server.config.settings")

    def get_settings(self):
        from scraperapi_mcp_server.config import settings

        return settings

    def with_settings(
        self,
        mock_settings,
        api_key="test_api_key",
        api_url="https://test.api.scraperapi.com",
        timeout=60,
    ):
        mock_settings.API_KEY = api_key
        mock_settings.API_URL = api_url
        mock_settings.API_TIMEOUT_SECONDS = timeout
        return self.get_settings()

    def test_config_from_environment(self, mock_settings):
        settings = self.with_settings(mock_settings)
        assert settings.API_KEY == "test_api_key"
        assert settings.API_URL == "https://test.api.scraperapi.com"
        assert settings.API_TIMEOUT_SECONDS == 60

    def test_config_defaults(self, mock_settings):
        settings = self.with_settings(
            mock_settings,
            api_key="default_key",
            api_url="https://api.scraperapi.com",
            timeout=70,
        )

        assert all(
            hasattr(settings, attr)
            for attr in ["API_KEY", "API_URL", "API_TIMEOUT_SECONDS"]
        )

        assert settings.API_KEY == "default_key"
        assert settings.API_URL == "https://api.scraperapi.com"
        assert settings.API_TIMEOUT_SECONDS == 70

    def test_config_invalid_timeout(self, mock_settings):
        settings = self.with_settings(mock_settings, timeout=30)
        assert (
            isinstance(settings.API_TIMEOUT_SECONDS, int)
            and settings.API_TIMEOUT_SECONDS == 30
        )

    @pytest.mark.parametrize("timeout", [30, 60, 120, 300])
    def test_config_timeout_values(self, mock_settings, timeout):
        settings = self.with_settings(mock_settings, timeout=timeout)
        assert settings.API_TIMEOUT_SECONDS == timeout
