import pytest
import requests as req
import config
from utils.api_client import ApiClient


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

    def test_token_sent_as_bearer_header(self, client: ApiClient, user_token: str):
        resp = req.post(
            f"{client.base_url}/api/auth/verify",
            headers={"Authorization": f"Bearer {user_token}"},
            timeout=config.TIMEOUT,
        )
        assert resp.status_code == 200, (
            f"Токен не принят. Статус: {resp.status_code}. Тело: {resp.text}"
        )

    def test_verify_invalid_token_has_error_message(self, client: ApiClient):
        resp = client.verify_token(token="bad.token.here")
        assert resp.status_code == 401
        body = resp.json()
        assert "detail" in body, f"Нет поля detail: {body}"
        assert len(body["detail"]) > 0
