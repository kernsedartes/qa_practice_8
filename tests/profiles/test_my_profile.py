import pytest
import config
from utils.api_client import ApiClient


class TestGetMyProfile:

    def test_user_can_get_own_profile_200(self, client: ApiClient, user_token: str):
        resp = client.get_my_profile(user_token)
        assert resp.status_code == 200, resp.text

    def test_admin_can_get_own_profile_200(self, client: ApiClient, admin_token: str):
        resp = client.get_my_profile(admin_token)
        assert resp.status_code == 200, resp.text

    def test_profile_response_structure(self, client: ApiClient, user_token: str):
        body = client.get_my_profile(user_token).json()
        assert "message" in body, f"Нет поля message: {body}"
        assert "profile" in body, f"Нет поля profile: {body}"
        profile = body["profile"]
        for field in ("id", "username", "email", "role", "is_active"):
            assert field in profile, f"Нет поля '{field}' в profile: {profile}"

    def test_profile_role_structure(self, client: ApiClient, user_token: str):
        profile = client.get_my_profile(user_token).json()["profile"]
        role = profile["role"]
        for field in ("id", "name", "description"):
            assert field in role, f"Нет поля '{field}' в role: {role}"

    def test_profile_values_match_login(self, client: ApiClient, user_token: str):
        profile = client.get_my_profile(user_token).json()["profile"]
        assert profile["username"] == config.USER_LOGIN, (
            f"Ожидался username='{config.USER_LOGIN}', получен '{profile['username']}'"
        )
        assert profile["role"]["name"] == "user", (
            f"Ожидалась роль 'user', получена '{profile['role']['name']}'"
        )
        assert profile["is_active"] is True

    def test_admin_profile_has_admin_role(self, client: ApiClient, admin_token: str):
        profile = client.get_my_profile(admin_token).json()["profile"]
        assert profile["role"]["name"] == "admin", (
            f"Ожидалась роль 'admin', получена '{profile['role']['name']}'"
        )

    def test_no_token_returns_403(self, client: ApiClient):
        resp = client.get_my_profile(token=None)
        assert resp.status_code == 403, f"Ожидался 403, получен {resp.status_code}"

    def test_invalid_token_returns_401(self, client: ApiClient):
        resp = client.get_my_profile(token="invalid.token.value")
        assert resp.status_code == 401, f"Ожидался 401, получен {resp.status_code}"

    def test_invalid_token_has_error_message(self, client: ApiClient):
        resp = client.get_my_profile(token="bad.token")
        assert resp.status_code == 401
        body = resp.json()
        assert "detail" in body, f"Нет поля detail: {body}"
        assert len(body["detail"]) > 0
