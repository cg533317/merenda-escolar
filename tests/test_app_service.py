from backend.services.app_service import AppService


def test_get_info():
    info = AppService.get_info()

    assert info["name"] == "AquaBot"
    assert info["environment"] == "development"
    assert info["debug"] is True
