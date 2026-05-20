import pytest
from utils.api_client import ApiClient


class TestDeleteProfile:

    def test_admin_can_delete_profile(
        self, client: ApiClient, admin_token: str, registered_user: dict
    ):
        account_id = registered_user["account_id"]
        assert account_id is not None

        resp = client.delete_profile(account_id, token=admin_token)
        assert resp.status_code == 200, (
            f"Ожидался 200, получен {resp.status_code}. Тело: {resp.text}"
        )
        registered_user["account_id"] = None

    def test_user_cannot_delete_profile_returns_403(
        self, client: ApiClient, user_token: str, registered_user: dict
    ):
        account_id = registered_user["account_id"]
        assert account_id is not None

        resp = client.delete_profile(account_id, token=user_token)
        assert resp.status_code == 403, (
            f"Ожидался 403, получен {resp.status_code}. Тело: {resp.text}"
        )

    def test_user_cannot_delete_error_message(
        self, client: ApiClient, user_token: str, registered_user: dict
    ):
        account_id = registered_user["account_id"]
        assert account_id is not None

        resp = client.delete_profile(account_id, token=user_token)
        assert resp.status_code == 403
        body = resp.json()
        assert "detail" in body, f"Нет поля detail: {body}"
        assert len(body["detail"]) > 0

    def test_no_token_returns_403(self, client: ApiClient):
        resp = client.delete_profile(account_id=1, token=None)
        assert resp.status_code == 403, f"Ожидался 403, получен {resp.status_code}"

    def test_invalid_token_returns_401(self, client: ApiClient):
        resp = client.delete_profile(account_id=1, token="bad.token")
        assert resp.status_code == 401, f"Ожидался 401, получен {resp.status_code}"
