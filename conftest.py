"""
Общие фикстуры pytest.
"""
import uuid
import pytest
from utils.api_client import ApiClient
import config


@pytest.fixture(scope="session")
def client() -> ApiClient:
    return ApiClient()


@pytest.fixture(scope="session")
def user_token(client: ApiClient) -> str:
    """JWT обычного пользователя."""
    return client.get_token(config.USER_LOGIN, config.USER_PASSWORD)


@pytest.fixture(scope="session")
def admin_token(client: ApiClient) -> str:
    """JWT администратора."""
    return client.get_token(config.ADMIN_LOGIN, config.ADMIN_PASSWORD)


@pytest.fixture(scope="session")
def registered_user(client: ApiClient) -> dict:
    """
    Регистрирует тестового пользователя один раз на сессию.
    Возвращает словарь {username, email, password}.
    """
    uid = uuid.uuid4().hex[:8]
    username = f"testuser_{uid}"
    email    = f"{username}@test.com"
    password = "TestPass123"
    resp = client.register(username, email, password)
    assert resp.status_code == 200, f"Не удалось зарегистрировать тестового юзера: {resp.text}"
    return {"username": username, "email": email, "password": password}


@pytest.fixture(scope="session")
def registered_user_token(client: ApiClient, registered_user: dict) -> str:
    """JWT зарегистрированного тестового пользователя."""
    return client.get_token(registered_user["username"], registered_user["password"])
