import uuid
import pytest
from utils.api_client import ApiClient
import config


@pytest.fixture(scope="session")
def client() -> ApiClient:
    return ApiClient()


@pytest.fixture(scope="session")
def user_token(client: ApiClient) -> str:
    return client.get_token(config.USER_LOGIN, config.USER_PASSWORD)


@pytest.fixture(scope="session")
def admin_token(client: ApiClient) -> str:
    return client.get_token(config.ADMIN_LOGIN, config.ADMIN_PASSWORD)


@pytest.fixture(scope="session")
def moderator_token(client: ApiClient, admin_token: str):
    uid = uuid.uuid4().hex[:8]
    username = f"moderator_{uid}"
    email = f"{username}@test.com"
    password = "ModerPass123"

    resp = client.register(username, email, password)
    assert resp.status_code == 200, f"Не удалось зарегистрировать модератора: {resp.text}"

    token = client.get_token(username, password)
    profile = client.get_my_profile(token).json()
    account_id = client.extract_account_id(profile)
    assert account_id is not None

    role_resp = client.update_account_role(account_id, "moderator", token=admin_token)
    assert role_resp.status_code == 200, f"Не удалось назначить роль модератора: {role_resp.text}"

    yield client.get_token(username, password)

    client.delete_profile(account_id, token=admin_token)


@pytest.fixture()
def registered_user(client: ApiClient, admin_token: str):
    uid = uuid.uuid4().hex[:8]
    username = f"testuser_{uid}"
    email = f"{username}@test.com"
    password = "TestPass123"

    resp = client.register(username, email, password)
    assert resp.status_code == 200, f"Не удалось зарегистрировать тестового юзера: {resp.text}"

    token = client.get_token(username, password)
    profile_resp = client.get_my_profile(token).json()
    account_id = client.extract_account_id(profile_resp)

    yield {"username": username, "email": email, "password": password, "account_id": account_id}

    if account_id:
        client.delete_profile(account_id, token=admin_token)
