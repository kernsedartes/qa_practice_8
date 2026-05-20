import pytest
import requests as req
import config
from utils.api_client import ApiClient


class TestLogin:

    @pytest.mark.parametrize("username, password, expected_status", [
        (config.USER_LOGIN,  config.USER_PASSWORD, 200),
        (config.ADMIN_LOGIN, config.ADMIN_PASSWORD, 200),
        (config.USER_LOGIN,  "wrong_password_xyz",  401),
        ("ghost_nobody_42",  "any_password",        401),
    ])
    def test_login_status_code(self, client: ApiClient, username, password, expected_status):
        resp = client.login(username, password)
        assert resp.status_code == expected_status, (
            f"username={username!r}: ожидался {expected_status}, получен {resp.status_code}. "
            f"Тело: {resp.text}"
        )

    @pytest.mark.parametrize("username, password", [
        ("", config.USER_PASSWORD),
        (config.USER_LOGIN, ""),
    ])
    def test_login_empty_fields_returns_422(self, client: ApiClient, username, password):
        resp = req.post(
            f"{client.base_url}/api/auth/login",
            json={"username": username, "password": password},
            timeout=config.TIMEOUT,
        )
        assert resp.status_code == 422, (
            f"Ожидался 422, получен {resp.status_code}"
        )

    def test_login_missing_body_returns_422(self, client: ApiClient):
        resp = req.post(
            f"{client.base_url}/api/auth/login",
            json={},
            timeout=config.TIMEOUT,
        )
        assert resp.status_code == 422, f"Ожидался 422, получен {resp.status_code}"

    def test_login_response_structure(self, client: ApiClient):
        body = client.login(config.USER_LOGIN, config.USER_PASSWORD).json()
        assert "access_token" in body, f"Нет access_token. Тело: {body}"
        assert "token_type"   in body, f"Нет token_type. Тело: {body}"
        assert "user"         in body, f"Нет user. Тело: {body}"

    def test_login_token_is_non_empty_string(self, client: ApiClient):
        token = client.login(config.USER_LOGIN, config.USER_PASSWORD).json()["access_token"]
        assert isinstance(token, str) and len(token) > 0

    def test_login_token_type_is_bearer(self, client: ApiClient):
        body = client.login(config.USER_LOGIN, config.USER_PASSWORD).json()
        assert body["token_type"].lower() == "bearer", (
            f"Ожидался token_type='bearer', получен '{body['token_type']}'"
        )

    def test_login_user_object_has_username(self, client: ApiClient):
        body = client.login(config.USER_LOGIN, config.USER_PASSWORD).json()
        assert "username" in body["user"], f"Нет username в user: {body['user']}"

    def test_login_wrong_password_error_message(self, client: ApiClient):
        resp = client.login(config.USER_LOGIN, "wrong_password_xyz")
        assert resp.status_code == 401
        body = resp.json()
        assert "detail" in body, f"Нет поля detail: {body}"
        assert "password" in body["detail"].lower() or "incorrect" in body["detail"].lower(), (
            f"Неожиданное сообщение: '{body['detail']}'"
        )
