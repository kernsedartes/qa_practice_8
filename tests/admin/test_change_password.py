import pytest
from utils.api_client import ApiClient


class TestChangePassword:

    def test_change_password_success(self, client: ApiClient, registered_user: dict):
        old_pass = registered_user["password"]
        new_pass = "NewTemporaryPass999"
        token = client.get_token(registered_user["username"], old_pass)

        resp = client.change_password(old_pass, new_pass, token=token)
        assert resp.status_code == 200, (
            f"Ожидался 200. Статус: {resp.status_code}. Тело: {resp.text}"
        )

        new_token = client.get_token(registered_user["username"], new_pass)
        assert new_token

    def test_wrong_old_password_returns_400(self, client: ApiClient, registered_user: dict):
        token = client.get_token(registered_user["username"], registered_user["password"])
        resp = client.change_password(
            old_password="completely_wrong_old_pass",
            new_password="NewPass123",
            token=token,
        )
        assert resp.status_code == 400, (
            f"Ожидался 400. Статус: {resp.status_code}. Тело: {resp.text}"
        )

    def test_wrong_old_password_error_message(self, client: ApiClient, registered_user: dict):
        token = client.get_token(registered_user["username"], registered_user["password"])
        resp = client.change_password("wrong_pass", "NewPass123", token=token)
        assert resp.status_code == 400
        body = resp.json()
        assert "detail" in body, f"Нет поля detail: {body}"
        assert "password" in body["detail"].lower() or "invalid" in body["detail"].lower(), (
            f"Неожиданное сообщение: '{body['detail']}'"
        )

    def test_no_token_returns_403(self, client: ApiClient):
        resp = client.change_password(old_password="old", new_password="new", token=None)
        assert resp.status_code == 403, f"Ожидался 403, получен {resp.status_code}"

    def test_invalid_token_returns_401(self, client: ApiClient):
        resp = client.change_password("old", "new", token="bad.token")
        assert resp.status_code == 401, f"Ожидался 401, получен {resp.status_code}"
