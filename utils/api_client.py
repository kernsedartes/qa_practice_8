"""
Клиент для Secure Authentication API (https://secby.ru)
Все пути взяты из OpenAPI-схемы.
"""
import requests
import config


class ApiClient:

    def __init__(self, base_url: str = config.BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    # ------------------------------------------------------------------
    # Authentication  —  /api/auth/*
    # ------------------------------------------------------------------

    def register(self, username: str, email: str, password: str) -> requests.Response:
        """POST /api/auth/register — регистрация нового аккаунта (роль: user)."""
        return self.session.post(
            f"{self.base_url}/api/auth/register",
            json={"username": username, "email": email, "password": password},
            timeout=config.TIMEOUT,
        )

    def login(self, username: str, password: str) -> requests.Response:
        """POST /api/auth/login — получение JWT-токена. Тело: application/json."""
        return self.session.post(
            f"{self.base_url}/api/auth/login",
            json={"username": username, "password": password},
            timeout=config.TIMEOUT,
        )

    def get_token(self, username: str, password: str) -> str:
        """Авторизуется и возвращает строку access_token."""
        resp = self.login(username, password)
        resp.raise_for_status()
        return resp.json()["access_token"]

    def verify_token(self, token: str | None = None) -> requests.Response:
        """POST /api/auth/verify — проверка валидности JWT."""
        return self.session.post(
            f"{self.base_url}/api/auth/verify",
            headers=self._bearer(token),
            timeout=config.TIMEOUT,
        )

    def change_password(
        self, old_password: str, new_password: str, token: str | None = None
    ) -> requests.Response:
        """POST /api/auth/change-password — смена пароля (требует токен)."""
        return self.session.post(
            f"{self.base_url}/api/auth/change-password",
            json={"old_password": old_password, "new_password": new_password},
            headers=self._bearer(token),
            timeout=config.TIMEOUT,
        )

    # ------------------------------------------------------------------
    # Profiles  —  /api/profiles/*
    # ------------------------------------------------------------------

    def get_my_profile(self, token: str | None = None) -> requests.Response:
        """GET /api/profiles/me — профиль текущего пользователя."""
        return self.session.get(
            f"{self.base_url}/api/profiles/me",
            headers=self._bearer(token),
            timeout=config.TIMEOUT,
        )

    def list_profiles(
        self, token: str | None = None, limit: int = 100, offset: int = 0
    ) -> requests.Response:
        """
        GET /api/profiles/ — список профилей.
        user видит только свой, moderator/admin — все.
        """
        return self.session.get(
            f"{self.base_url}/api/profiles/",
            headers=self._bearer(token),
            params={"limit": limit, "offset": offset},
            timeout=config.TIMEOUT,
        )

    def get_profile_by_id(self, account_id: int, token: str | None = None) -> requests.Response:
        """GET /api/profiles/{account_id} — профиль по ID."""
        return self.session.get(
            f"{self.base_url}/api/profiles/{account_id}",
            headers=self._bearer(token),
            timeout=config.TIMEOUT,
        )

    def create_profile(self, token: str | None = None, **fields) -> requests.Response:
        """POST /api/profiles/ — создать профиль для текущего пользователя."""
        return self.session.post(
            f"{self.base_url}/api/profiles/",
            json=fields,
            headers=self._bearer(token),
            timeout=config.TIMEOUT,
        )

    def update_my_profile(self, token: str | None = None, **fields) -> requests.Response:
        """PUT /api/profiles/me — обновить свой профиль."""
        return self.session.put(
            f"{self.base_url}/api/profiles/me",
            json=fields,
            headers=self._bearer(token),
            timeout=config.TIMEOUT,
        )

    def update_account_role(
        self, account_id: int, role_name: str, token: str | None = None
    ) -> requests.Response:
        """PUT /api/profiles/{account_id}/role?role_name=... — смена роли (только admin)."""
        return self.session.put(
            f"{self.base_url}/api/profiles/{account_id}/role",
            headers=self._bearer(token),
            params={"role_name": role_name},
            timeout=config.TIMEOUT,
        )

    def delete_profile(self, account_id: int, token: str | None = None) -> requests.Response:
        """DELETE /api/profiles/{account_id} — удалить профиль (только admin)."""
        return self.session.delete(
            f"{self.base_url}/api/profiles/{account_id}",
            headers=self._bearer(token),
            timeout=config.TIMEOUT,
        )

    def update_profile_by_id(
        self, account_id: int, token: str | None = None, **fields
    ) -> requests.Response:
        """PUT /api/profiles/{account_id} — обновить профиль по ID (moderator/admin)."""
        return self.session.put(
            f"{self.base_url}/api/profiles/{account_id}",
            json=fields,
            headers=self._bearer(token),
            timeout=config.TIMEOUT,
        )

    # ------------------------------------------------------------------
    # Auth (дополнительные)  —  /api/auth/*
    # ------------------------------------------------------------------

    def reset_password(self, username: str, new_password: str) -> requests.Response:
        """POST /api/auth/reset-password — сброс пароля без старого (без токена)."""
        return self.session.post(
            f"{self.base_url}/api/auth/reset-password",
            json={"username": username, "new_password": new_password},
            timeout=config.TIMEOUT,
        )

    # ------------------------------------------------------------------
    # Notes  —  /api/notes/*
    # ------------------------------------------------------------------

    def list_notes(
        self, token: str | None = None, limit: int = 100, offset: int = 0
    ) -> requests.Response:
        """GET /api/notes/ — список ресурсов (без контента)."""
        return self.session.get(
            f"{self.base_url}/api/notes/",
            headers=self._bearer(token),
            params={"limit": limit, "offset": offset},
            timeout=config.TIMEOUT,
        )

    def create_note(
        self,
        name: str,
        notes: str,
        type: str,
        token: str | None = None,
        role_id: int | None = None,
    ) -> requests.Response:
        """POST /api/notes/ — создать ресурс (→ 201). type: public | private | role."""
        payload: dict = {"name": name, "notes": notes, "type": type}
        if role_id is not None:
            payload["role_id"] = role_id
        return self.session.post(
            f"{self.base_url}/api/notes/",
            json=payload,
            headers=self._bearer(token),
            timeout=config.TIMEOUT,
        )

    def get_note(self, resource_id: int, token: str | None = None) -> requests.Response:
        """GET /api/notes/{resource_id} — ресурс с полным контентом."""
        return self.session.get(
            f"{self.base_url}/api/notes/{resource_id}",
            headers=self._bearer(token),
            timeout=config.TIMEOUT,
        )

    def update_note(
        self,
        resource_id: int,
        name: str,
        notes: str,
        type: str,
        token: str | None = None,
        role_id: int | None = None,
    ) -> requests.Response:
        """PUT /api/notes/{resource_id} — обновить ресурс."""
        payload: dict = {"name": name, "notes": notes, "type": type}
        if role_id is not None:
            payload["role_id"] = role_id
        return self.session.put(
            f"{self.base_url}/api/notes/{resource_id}",
            json=payload,
            headers=self._bearer(token),
            timeout=config.TIMEOUT,
        )

    def delete_note(self, resource_id: int, token: str | None = None) -> requests.Response:
        """DELETE /api/notes/{resource_id} — удалить ресурс (→ 204)."""
        return self.session.delete(
            f"{self.base_url}/api/notes/{resource_id}",
            headers=self._bearer(token),
            timeout=config.TIMEOUT,
        )

    # ------------------------------------------------------------------
    # Вспомогательное
    # ------------------------------------------------------------------

    @staticmethod
    def _bearer(token: str | None) -> dict:
        if token is None:
            return {}
        return {"Authorization": f"Bearer {token}"}
