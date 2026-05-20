import pytest
from utils.api_client import ApiClient


class TestChangeRole:

    def test_admin_can_change_role_to_moderator(
        self, client: ApiClient, admin_token: str, registered_user: dict
    ):
        account_id = registered_user["account_id"]
        assert account_id is not None

        resp = client.update_account_role(account_id, "moderator", token=admin_token)
        assert resp.status_code == 200, (
            f"Ожидался 200, получен {resp.status_code}. Тело: {resp.text}"
        )

    def test_user_cannot_change_role_returns_403(
        self, client: ApiClient, user_token: str, registered_user: dict
    ):
        account_id = registered_user["account_id"]
        assert account_id is not None

        resp = client.update_account_role(account_id, "admin", token=user_token)
        assert resp.status_code == 403, (
            f"Ожидался 403, получен {resp.status_code}. Тело: {resp.text}"
        )

    def test_user_cannot_change_role_error_message(
        self, client: ApiClient, user_token: str, registered_user: dict
    ):
        account_id = registered_user["account_id"]
        assert account_id is not None

        resp = client.update_account_role(account_id, "admin", token=user_token)
        assert resp.status_code == 403
        body = resp.json()
        assert "detail" in body, f"Нет поля detail: {body}"
        assert len(body["detail"]) > 0

    @pytest.mark.parametrize("role_name", ["user", "moderator", "admin"])
    def test_admin_can_assign_any_role(
        self, client: ApiClient, admin_token: str, registered_user: dict, role_name: str
    ):
        account_id = registered_user["account_id"]
        assert account_id is not None

        resp = client.update_account_role(account_id, role_name, token=admin_token)
        assert resp.status_code == 200, (
            f"role_name={role_name!r}: ожидался 200, получен {resp.status_code}. "
            f"Тело: {resp.text}"
        )

    def test_no_token_returns_403(self, client: ApiClient):
        resp = client.update_account_role(account_id=1, role_name="user", token=None)
        assert resp.status_code == 403, f"Ожидался 403, получен {resp.status_code}"

    def test_invalid_token_returns_401(self, client: ApiClient):
        resp = client.update_account_role(
            account_id=1, role_name="user", token="bad.token.value"
        )
        assert resp.status_code == 401, f"Ожидался 401, получен {resp.status_code}"
