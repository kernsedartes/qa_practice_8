import uuid
import pytest
from utils.api_client import ApiClient
import config


class TestRegister:

    def test_register_new_user_returns_200(self, client: ApiClient):
        uid = uuid.uuid4().hex[:8]
        resp = client.register(f"newuser_{uid}", f"newuser_{uid}@test.com", "Password1")
        assert resp.status_code == 200, resp.text

    def test_register_response_has_expected_keys(self, client: ApiClient):
        uid = uuid.uuid4().hex[:8]
        resp = client.register(f"keytest_{uid}", f"keytest_{uid}@test.com", "Password1")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, dict) and len(body) > 0, f"Пустой ответ: {body}"

    def test_register_duplicate_username_fails(self, client: ApiClient, registered_user: dict):
        resp = client.register(
            registered_user["username"],
            f"other_{uuid.uuid4().hex[:6]}@test.com",
            "Password1",
        )
        assert resp.status_code != 200, "Ожидалась ошибка при дубликате username"

    def test_register_duplicate_email_fails(self, client: ApiClient, registered_user: dict):
        resp = client.register(
            f"unique_{uuid.uuid4().hex[:6]}",
            registered_user["email"],
            "Password1",
        )
        assert resp.status_code != 200, "Ожидалась ошибка при дубликате email"

    def test_register_missing_fields_returns_422(self, client: ApiClient):
        import requests as req
        resp = req.post(
            f"{client.base_url}/api/auth/register",
            json={"username": "onlyname"},
            timeout=config.TIMEOUT,
        )
        assert resp.status_code == 422, f"Ожидался 422, получен {resp.status_code}"

    def test_register_invalid_email_returns_422(self, client: ApiClient):
        resp = client.register("someuser", "not-an-email", "Password1")
        assert resp.status_code == 422, f"Ожидался 422, получен {resp.status_code}"


class TestLogin:

    def test_login_user_returns_200(self, client: ApiClient):
        resp = client.login(config.USER_LOGIN, config.USER_PASSWORD)
        assert resp.status_code == 200, resp.text

    def test_login_admin_returns_200(self, client: ApiClient):
        resp = client.login(config.ADMIN_LOGIN, config.ADMIN_PASSWORD)
        assert resp.status_code == 200, resp.text

    def test_login_response_has_access_token(self, client: ApiClient):
        body = client.login(config.USER_LOGIN, config.USER_PASSWORD).json()
        assert "access_token" in body, f"Нет access_token. Тело: {body}"

    def test_login_response_has_token_type(self, client: ApiClient):
        body = client.login(config.USER_LOGIN, config.USER_PASSWORD).json()
        assert "token_type" in body, f"Нет token_type. Тело: {body}"

    def test_login_response_has_user_object(self, client: ApiClient):
        body = client.login(config.USER_LOGIN, config.USER_PASSWORD).json()
        assert "user" in body and isinstance(body["user"], dict), (
            f"Нет объекта user. Тело: {body}"
        )

    def test_login_token_is_non_empty_string(self, client: ApiClient):
        token = client.login(config.USER_LOGIN, config.USER_PASSWORD).json()["access_token"]
        assert isinstance(token, str) and len(token) > 0

    def test_login_wrong_password_returns_401(self, client: ApiClient):
        resp = client.login(config.USER_LOGIN, "wrong_password_xyz")
        assert resp.status_code == 401, f"Ожидался 401, получен {resp.status_code}"

    def test_login_nonexistent_user_returns_401(self, client: ApiClient):
        resp = client.login("ghost_nobody_42", "any_password")
        assert resp.status_code == 401, f"Ожидался 401, получен {resp.status_code}"

    def test_login_missing_fields_returns_422(self, client: ApiClient):
        import requests as req
        resp = req.post(
            f"{client.base_url}/api/auth/login",
            json={},
            timeout=config.TIMEOUT,
        )
        assert resp.status_code == 422, f"Ожидался 422, получен {resp.status_code}"

    def test_login_empty_username_returns_422(self, client: ApiClient):
        import requests as req
        resp = req.post(
            f"{client.base_url}/api/auth/login",
            json={"username": "", "password": config.USER_PASSWORD},
            timeout=config.TIMEOUT,
        )
        assert resp.status_code != 200, "Ожидалась ошибка при пустом username"


class TestVerifyToken:

    def test_verify_valid_user_token_returns_200(self, client: ApiClient, user_token: str):
        resp = client.verify_token(user_token)
        assert resp.status_code == 200, resp.text

    def test_verify_valid_admin_token_returns_200(self, client: ApiClient, admin_token: str):
        resp = client.verify_token(admin_token)
        assert resp.status_code == 200, resp.text

    def test_verify_response_is_not_empty(self, client: ApiClient, user_token: str):
        body = client.verify_token(user_token).json()
        assert isinstance(body, dict) and len(body) > 0, f"Пустой ответ: {body}"

    def test_verify_no_token_returns_403(self, client: ApiClient):
        resp = client.verify_token(token=None)
        assert resp.status_code == 403, f"Ожидался 403, получен {resp.status_code}"

    def test_verify_invalid_token_returns_401(self, client: ApiClient):
        resp = client.verify_token(token="this.is.not.valid.jwt")
        assert resp.status_code == 401, f"Ожидался 401, получен {resp.status_code}"

    def test_token_is_sent_as_bearer(self, client: ApiClient, user_token: str):
        import requests as req
        resp = req.post(
            f"{client.base_url}/api/auth/verify",
            headers={"Authorization": f"Bearer {user_token}"},
            timeout=config.TIMEOUT,
        )
        assert resp.status_code == 200, (
            f"Токен не принят сервером. Статус: {resp.status_code}. Тело: {resp.text}"
        )
