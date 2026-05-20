import pytest
from utils.api_client import ApiClient


class TestProfileAccessControl:

    def test_user_cannot_access_other_profile(
        self, client: ApiClient, user_token: str, admin_token: str
    ):
        admin_profile = client.get_my_profile(admin_token).json()
        admin_id = client.extract_account_id(admin_profile)
        assert admin_id is not None

        resp = client.get_profile_by_id(admin_id, token=user_token)
        assert resp.status_code == 403, (
            f"Ожидался 403, получен {resp.status_code}. Тело: {resp.text}"
        )

    def test_user_cannot_access_other_profile_error_message(
        self, client: ApiClient, user_token: str, admin_token: str
    ):
        admin_profile = client.get_my_profile(admin_token).json()
        admin_id = client.extract_account_id(admin_profile)
        assert admin_id is not None

        resp = client.get_profile_by_id(admin_id, token=user_token)
        assert resp.status_code == 403
        body = resp.json()
        assert "detail" in body, f"Нет поля detail: {body}"
        assert len(body["detail"]) > 0

    def test_admin_can_access_user_profile(
        self, client: ApiClient, admin_token: str, user_token: str
    ):
        user_profile = client.get_my_profile(user_token).json()
        user_id = client.extract_account_id(user_profile)
        assert user_id is not None

        resp = client.get_profile_by_id(user_id, token=admin_token)
        assert resp.status_code == 200, (
            f"Ожидался 200, получен {resp.status_code}. Тело: {resp.text}"
        )

    def test_admin_profile_by_id_response_structure(
        self, client: ApiClient, admin_token: str, user_token: str
    ):
        user_profile_data = client.get_my_profile(user_token).json()
        user_id = client.extract_account_id(user_profile_data)
        assert user_id is not None

        resp = client.get_profile_by_id(user_id, token=admin_token)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        profile = body.get("profile", body)
        for field in ("id", "username", "email", "role", "is_active"):
            assert field in profile, f"Нет поля '{field}' в ответе: {profile}"
        assert profile["id"] == user_id, (
            f"id профиля не совпадает: ожидался {user_id}, получен {profile['id']}"
        )
        assert profile["username"] == user_profile_data.get("profile", user_profile_data).get("username"), (
            f"username не совпадает с данными из /me: {profile}"
        )
        assert profile["is_active"] is True, (
            f"Ожидался is_active=True: {profile}"
        )

    def test_no_token_returns_403(self, client: ApiClient):
        resp = client.get_profile_by_id(account_id=1, token=None)
        assert resp.status_code == 403, f"Ожидался 403, получен {resp.status_code}"
