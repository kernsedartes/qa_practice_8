import requests
import config


class ApiClient:

    def __init__(self, base_url: str = config.BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def register(self, username: str, email: str, password: str) -> requests.Response:
        return self.session.post(
            f"{self.base_url}/api/auth/register",
            json={"username": username, "email": email, "password": password},
            timeout=config.TIMEOUT,
        )

    def login(self, username: str, password: str) -> requests.Response:
        return self.session.post(
            f"{self.base_url}/api/auth/login",
            json={"username": username, "password": password},
            timeout=config.TIMEOUT,
        )

    def get_token(self, username: str, password: str) -> str:
        resp = self.login(username, password)
        resp.raise_for_status()
        return resp.json()["access_token"]

    def verify_token(self, token: str | None = None) -> requests.Response:
        return self.session.post(
            f"{self.base_url}/api/auth/verify",
            headers=self._bearer(token),
            timeout=config.TIMEOUT,
        )

    def change_password(
        self, old_password: str, new_password: str, token: str | None = None
    ) -> requests.Response:
        return self.session.post(
            f"{self.base_url}/api/auth/change-password",
            json={"old_password": old_password, "new_password": new_password},
            headers=self._bearer(token),
            timeout=config.TIMEOUT,
        )

    def get_my_profile(self, token: str | None = None) -> requests.Response:
        return self.session.get(
            f"{self.base_url}/api/profiles/me",
            headers=self._bearer(token),
            timeout=config.TIMEOUT,
        )

    def list_profiles(
        self, token: str | None = None, limit: int = 100, offset: int = 0
    ) -> requests.Response:
        return self.session.get(
            f"{self.base_url}/api/profiles/",
            headers=self._bearer(token),
            params={"limit": limit, "offset": offset},
            timeout=config.TIMEOUT,
        )

    def get_profile_by_id(self, account_id: int, token: str | None = None) -> requests.Response:
        return self.session.get(
            f"{self.base_url}/api/profiles/{account_id}",
            headers=self._bearer(token),
            timeout=config.TIMEOUT,
        )

    def update_profile_by_id(
        self, account_id: int, token: str | None = None, **fields
    ) -> requests.Response:
        return self.session.put(
            f"{self.base_url}/api/profiles/{account_id}",
            json=fields,
            headers=self._bearer(token),
            timeout=config.TIMEOUT,
        )

    def update_account_role(
        self, account_id: int, role_name: str, token: str | None = None
    ) -> requests.Response:
        return self.session.put(
            f"{self.base_url}/api/profiles/{account_id}/role",
            headers=self._bearer(token),
            params={"role_name": role_name},
            timeout=config.TIMEOUT,
        )

    def delete_profile(self, account_id: int, token: str | None = None) -> requests.Response:
        return self.session.delete(
            f"{self.base_url}/api/profiles/{account_id}",
            headers=self._bearer(token),
            timeout=config.TIMEOUT,
        )

    @staticmethod
    def _bearer(token: str | None) -> dict:
        if token is None:
            return {}
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def extract_account_id(profile_response: dict) -> int | None:
        profile = profile_response.get("profile", profile_response)
        return profile.get("id")
