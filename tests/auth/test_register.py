import uuid
import pytest
import requests as req
import config
from utils.api_client import ApiClient


@pytest.fixture()
def new_user(client: ApiClient, admin_token: str):
    uid = uuid.uuid4().hex[:8]
    username = f"newuser_{uid}"
    email = f"{username}@test.com"
    password = "Password1"

    resp = client.register(username, email, password)
    assert resp.status_code == 200, f"Регистрация не удалась: {resp.text}"

    token = client.get_token(username, password)
    profile = client.get_my_profile(token).json()
    account_id = client.extract_account_id(profile)

    yield {"username": username, "email": email, "password": password,
           "account_id": account_id, "register_response": resp}

    if account_id:
        client.delete_profile(account_id, token=admin_token)


class TestRegister:

    def test_register_new_user_returns_200(self, new_user: dict):
        assert new_user["register_response"].status_code == 200, (
            new_user["register_response"].text
        )

    def test_register_response_is_non_empty_dict(self, new_user: dict):
        body = new_user["register_response"].json()
        assert isinstance(body, dict) and len(body) > 0, f"Пустой ответ: {body}"

    def test_register_duplicate_username_returns_400(
        self, client: ApiClient, registered_user: dict
    ):
        resp = client.register(
            registered_user["username"],
            f"other_{uuid.uuid4().hex[:6]}@test.com",
            "Password1",
        )
        assert resp.status_code == 400, (
            f"Ожидался 400, получен {resp.status_code}. Тело: {resp.text}"
        )

    def test_register_duplicate_email_returns_400(
        self, client: ApiClient, registered_user: dict
    ):
        resp = client.register(
            f"unique_{uuid.uuid4().hex[:6]}",
            registered_user["email"],
            "Password1",
        )
        assert resp.status_code == 400, (
            f"Ожидался 400, получен {resp.status_code}. Тело: {resp.text}"
        )

    def test_register_duplicate_username_has_error_message(
        self, client: ApiClient, registered_user: dict
    ):
        resp = client.register(
            registered_user["username"],
            f"other2_{uuid.uuid4().hex[:6]}@test.com",
            "Password1",
        )
        body = resp.json()
        assert "detail" in body, f"Нет поля detail: {body}"
        assert len(body["detail"]) > 0

    @pytest.mark.parametrize("payload", [
        {"username": "onlyname"},
        {"email": "only@test.com"},
        {"password": "OnlyPass1"},
        {"username": "partial", "email": "partial@test.com"},
        {"username": "partial", "password": "PartPass1"},
    ])
    def test_register_missing_required_fields_returns_422(
        self, client: ApiClient, payload: dict
    ):
        resp = req.post(
            f"{client.base_url}/api/auth/register",
            json=payload,
            timeout=config.TIMEOUT,
        )
        assert resp.status_code == 422, (
            f"payload={payload}: ожидался 422, получен {resp.status_code}"
        )

    def test_register_invalid_email_returns_422(self, client: ApiClient):
        resp = client.register("someuser", "not-an-email", "Password1")
        assert resp.status_code == 422, f"Ожидался 422, получен {resp.status_code}"
