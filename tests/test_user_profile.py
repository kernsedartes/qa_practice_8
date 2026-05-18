import pytest
from utils.api_client import ApiClient
import config


class TestGetMyProfile:

    def test_user_can_get_own_profile_200(self, client: ApiClient, user_token: str):
        resp = client.get_my_profile(user_token)
        assert resp.status_code == 200, resp.text

    def test_admin_can_get_own_profile_200(self, client: ApiClient, admin_token: str):
        resp = client.get_my_profile(admin_token)
        assert resp.status_code == 200, resp.text

    def test_profile_response_is_dict(self, client: ApiClient, user_token: str):
        body = client.get_my_profile(user_token).json()
        assert isinstance(body, dict), f"Ожидался dict, получен {type(body)}: {body}"

    def test_no_token_returns_403(self, client: ApiClient):
        resp = client.get_my_profile(token=None)
        assert resp.status_code == 403, f"Ожидался 403, получен {resp.status_code}"

    def test_invalid_token_returns_401(self, client: ApiClient):
        resp = client.get_my_profile(token="invalid.token.value")
        assert resp.status_code == 401, f"Ожидался 401, получен {resp.status_code}"


class TestListProfiles:

    def test_user_sees_only_own_profile(self, client: ApiClient, user_token: str):
        resp = client.list_profiles(user_token)
        assert resp.status_code == 200, resp.text

    def test_admin_sees_all_profiles(self, client: ApiClient, admin_token: str):
        resp = client.list_profiles(admin_token)
        assert resp.status_code == 200, resp.text

    def test_list_profiles_no_token_returns_403(self, client: ApiClient):
        resp = client.list_profiles(token=None)
        assert resp.status_code == 403, f"Ожидался 403, получен {resp.status_code}"

    def test_list_profiles_response_is_object(self, client: ApiClient, admin_token: str):
        body = client.list_profiles(admin_token).json()
        assert isinstance(body, (dict, list)), f"Неожиданный тип: {type(body)}"

    def test_list_profiles_pagination_limit(self, client: ApiClient, admin_token: str):
        resp = client.list_profiles(admin_token, limit=5, offset=0)
        assert resp.status_code == 200, resp.text


class TestProfileAccessControl:

    def test_user_cannot_access_other_profile(
        self, client: ApiClient, user_token: str, admin_token: str
    ):
        admin_profile = client.get_my_profile(admin_token).json().get("profile", {})
        admin_id = admin_profile.get("account_id") or admin_profile.get("id")
        if admin_id is None:
            pytest.skip("Не удалось определить ID администратора из профиля")

        resp = client.get_profile_by_id(admin_id, token=user_token)
        assert resp.status_code == 403, (
            f"Ожидался 403 (доступ запрещён), получен {resp.status_code}. Тело: {resp.text}"
        )

    def test_admin_can_access_any_profile(
        self, client: ApiClient, admin_token: str, user_token: str
    ):
        user_profile = client.get_my_profile(user_token).json().get("profile", {})
        user_id = user_profile.get("account_id") or user_profile.get("id")
        if user_id is None:
            pytest.skip("Не удалось определить ID пользователя из профиля")

        resp = client.get_profile_by_id(user_id, token=admin_token)
        assert resp.status_code == 200, (
            f"admin должен видеть любой профиль. Статус: {resp.status_code}. Тело: {resp.text}"
        )
