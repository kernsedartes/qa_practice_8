import pytest
from utils.api_client import ApiClient


class TestModeratorProfiles:

    def test_verify_token_returns_200(self, client: ApiClient, moderator_token: str):
        resp = client.verify_token(moderator_token)
        assert resp.status_code == 200, resp.text

    def test_get_own_profile_returns_200(self, client: ApiClient, moderator_token: str):
        resp = client.get_my_profile(moderator_token)
        assert resp.status_code == 200, resp.text

    def test_profile_has_moderator_role(self, client: ApiClient, moderator_token: str):
        profile = client.get_my_profile(moderator_token).json()["profile"]
        assert profile["role"]["name"] == "moderator", (
            f"Ожидалась роль 'moderator', получена '{profile['role']['name']}'"
        )

    def test_list_profiles_returns_200(self, client: ApiClient, moderator_token: str):
        resp = client.list_profiles(moderator_token)
        assert resp.status_code == 200, resp.text

    def test_list_profiles_response_structure(self, client: ApiClient, moderator_token: str):
        resp = client.list_profiles(moderator_token)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert isinstance(body, dict), (
            f"Ожидался словарь, получен {type(body).__name__}: {body}"
        )

    def test_can_access_any_profile_by_id(
        self, client: ApiClient, moderator_token: str, registered_user: dict
    ):
        account_id = registered_user["account_id"]
        assert account_id is not None

        resp = client.get_profile_by_id(account_id, token=moderator_token)
        assert resp.status_code == 200, (
            f"Ожидался 200, получен {resp.status_code}. Тело: {resp.text}"
        )

    def test_profile_by_id_response_structure(
        self, client: ApiClient, moderator_token: str, registered_user: dict
    ):
        account_id = registered_user["account_id"]
        assert account_id is not None

        resp = client.get_profile_by_id(account_id, token=moderator_token)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        profile = body.get("profile", body)
        for field in ("id", "username", "email", "role", "is_active"):
            assert field in profile, f"Нет поля '{field}' в ответе: {profile}"
        assert profile["id"] == account_id, (
            f"id профиля не совпадает: ожидался {account_id}, получен {profile['id']}"
        )
        assert profile["username"] == registered_user["username"], (
            f"username не совпадает: ожидался '{registered_user['username']}', "
            f"получен '{profile['username']}'"
        )

    def test_can_update_any_profile(
        self, client: ApiClient, moderator_token: str, registered_user: dict
    ):
        account_id = registered_user["account_id"]
        assert account_id is not None

        resp = client.update_profile_by_id(
            account_id, token=moderator_token, about="Обновлено модератором"
        )
        assert resp.status_code == 200, (
            f"Ожидался 200, получен {resp.status_code}. Тело: {resp.text}"
        )

    def test_cannot_delete_profile(
        self, client: ApiClient, moderator_token: str, registered_user: dict
    ):
        account_id = registered_user["account_id"]
        assert account_id is not None

        resp = client.delete_profile(account_id, token=moderator_token)
        assert resp.status_code == 403, (
            f"Ожидался 403, получен {resp.status_code}. Тело: {resp.text}"
        )

    def test_cannot_delete_profile_error_message(
        self, client: ApiClient, moderator_token: str, registered_user: dict
    ):
        account_id = registered_user["account_id"]
        assert account_id is not None

        resp = client.delete_profile(account_id, token=moderator_token)
        assert resp.status_code == 403
        body = resp.json()
        assert "detail" in body, f"Нет поля detail: {body}"
        assert len(body["detail"]) > 0

    def test_cannot_change_role(
        self, client: ApiClient, moderator_token: str, registered_user: dict
    ):
        account_id = registered_user["account_id"]
        assert account_id is not None

        resp = client.update_account_role(account_id, "admin", token=moderator_token)
        assert resp.status_code == 403, (
            f"Ожидался 403, получен {resp.status_code}. Тело: {resp.text}"
        )

    def test_cannot_change_role_error_message(
        self, client: ApiClient, moderator_token: str, registered_user: dict
    ):
        account_id = registered_user["account_id"]
        assert account_id is not None

        resp = client.update_account_role(account_id, "admin", token=moderator_token)
        assert resp.status_code == 403
        body = resp.json()
        assert "detail" in body, f"Нет поля detail: {body}"
        assert len(body["detail"]) > 0
