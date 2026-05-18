import uuid
import pytest
from utils.api_client import ApiClient
import config


class TestChangeRole:

    def test_admin_can_change_role_to_moderator(
        self, client: ApiClient, admin_token: str, registered_user: dict
    ):
        token = client.get_token(registered_user["username"], registered_user["password"])
        profile = client.get_my_profile(token).json().get("profile", {})
        account_id = profile.get("account_id") or profile.get("id")
        if account_id is None:
            pytest.skip("Не удалось определить ID тестового пользователя")

        resp = client.update_account_role(account_id, "moderator", token=admin_token)
        assert resp.status_code == 200, (
            f"admin должен мочь менять роль → 200. "
            f"Статус: {resp.status_code}. Тело: {resp.text}"
        )

        client.update_account_role(account_id, "user", token=admin_token)

    def test_user_cannot_change_role(
        self, client: ApiClient, user_token: str, registered_user: dict
    ):
        token = client.get_token(registered_user["username"], registered_user["password"])
        profile = client.get_my_profile(token).json().get("profile", {})
        account_id = profile.get("account_id") or profile.get("id")
        if account_id is None:
            pytest.skip("Не удалось определить ID тестового пользователя")

        resp = client.update_account_role(account_id, "admin", token=user_token)
        assert resp.status_code == 403, (
            f"user не должен менять роли → 403. "
            f"Статус: {resp.status_code}. Тело: {resp.text}"
        )

    def test_change_role_no_token_returns_403(self, client: ApiClient):
        resp = client.update_account_role(account_id=1, role_name="user", token=None)
        assert resp.status_code == 403, f"Ожидался 403, получен {resp.status_code}"

    def test_change_role_invalid_token_returns_401(self, client: ApiClient):
        resp = client.update_account_role(
            account_id=1, role_name="user", token="bad.token.value"
        )
        assert resp.status_code == 401, f"Ожидался 401, получен {resp.status_code}"


class TestDeleteProfile:

    def test_user_cannot_delete_profile(
        self, client: ApiClient, user_token: str, admin_token: str
    ):
        admin_profile = client.get_my_profile(admin_token).json().get("profile", {})
        admin_id = admin_profile.get("account_id") or admin_profile.get("id")
        if admin_id is None:
            pytest.skip("Не удалось определить ID администратора")

        resp = client.delete_profile(admin_id, token=user_token)
        assert resp.status_code == 403, (
            f"user не должен удалять профили → 403. "
            f"Статус: {resp.status_code}. Тело: {resp.text}"
        )

    def test_delete_nonexistent_profile_as_admin(
        self, client: ApiClient, admin_token: str
    ):
        resp = client.delete_profile(account_id=999999, token=admin_token)
        assert resp.status_code in (404, 500), (
            f"Ожидался 404 или 500 для несуществующего аккаунта. "
            f"Статус: {resp.status_code}. Тело: {resp.text}"
        )

    def test_delete_no_token_returns_403(self, client: ApiClient):
        resp = client.delete_profile(account_id=1, token=None)
        assert resp.status_code == 403, f"Ожидался 403, получен {resp.status_code}"


class TestChangePassword:

    def test_change_password_wrong_old_password_returns_401(
        self, client: ApiClient, user_token: str
    ):
        resp = client.change_password(
            old_password="completely_wrong_old_pass",
            new_password="NewPass123",
            token=user_token,
        )
        assert resp.status_code in (400, 401), (
            f"Ожидался 400 или 401 при неверном старом пароле. "
            f"Статус: {resp.status_code}. Тело: {resp.text}"
        )

    def test_change_password_no_token_returns_403(self, client: ApiClient):
        resp = client.change_password(
            old_password="old", new_password="new", token=None
        )
        assert resp.status_code == 403, f"Ожидался 403, получен {resp.status_code}"

    def test_change_password_success_and_revert(
        self, client: ApiClient, registered_user: dict
    ):
        old_pass = registered_user["password"]
        new_pass = "NewTemporaryPass999"
        token = client.get_token(registered_user["username"], old_pass)

        resp = client.change_password(old_pass, new_pass, token=token)
        assert resp.status_code == 200, (
            f"Ожидался 200. Статус: {resp.status_code}. Тело: {resp.text}"
        )

        new_token = client.get_token(registered_user["username"], new_pass)
        assert new_token, "Не удалось авторизоваться с новым паролем"

        client.change_password(new_pass, old_pass, token=new_token)
