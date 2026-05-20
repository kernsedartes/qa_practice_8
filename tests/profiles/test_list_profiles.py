import pytest
from utils.api_client import ApiClient


class TestListProfiles:

    def test_user_can_list_profiles_200(self, client: ApiClient, user_token: str):
        resp = client.list_profiles(user_token)
        assert resp.status_code == 200, resp.text

    def test_admin_can_list_profiles_200(self, client: ApiClient, admin_token: str):
        resp = client.list_profiles(admin_token)
        assert resp.status_code == 200, resp.text

    def test_list_profiles_response_structure(self, client: ApiClient, admin_token: str):
        resp = client.list_profiles(admin_token)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert isinstance(body, dict), (
            f"Ожидался словарь, получен {type(body).__name__}: {body}"
        )

    def test_admin_list_profiles_items_have_required_fields(
        self, client: ApiClient, admin_token: str
    ):
        resp = client.list_profiles(admin_token)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "profiles" in body, (
            f"Нет ключа 'profiles' в ответе. Ключи: {list(body.keys())}"
        )
        profiles_list = body["profiles"]
        assert isinstance(profiles_list, list), (
            f"profiles должен быть списком, получен {type(profiles_list).__name__}"
        )
        assert len(profiles_list) > 0, "Список профилей пуст"
        for item in profiles_list:
            for field in ("id", "username", "email"):
                assert field in item, (
                    f"Нет поля '{field}' в элементе списка профилей: {item}"
                )

    def test_no_token_returns_403(self, client: ApiClient):
        resp = client.list_profiles(token=None)
        assert resp.status_code == 403, f"Ожидался 403, получен {resp.status_code}"

    def test_invalid_token_returns_401(self, client: ApiClient):
        resp = client.list_profiles(token="bad.token")
        assert resp.status_code == 401, f"Ожидался 401, получен {resp.status_code}"

    @pytest.mark.parametrize("limit, offset", [
        (5,   0),
        (10,  0),
        (100, 0),
        (5,   5),
    ])
    def test_pagination_params_accepted(
        self, client: ApiClient, admin_token: str, limit: int, offset: int
    ):
        resp = client.list_profiles(admin_token, limit=limit, offset=offset)
        assert resp.status_code == 200, (
            f"limit={limit}, offset={offset}: статус {resp.status_code}"
        )
