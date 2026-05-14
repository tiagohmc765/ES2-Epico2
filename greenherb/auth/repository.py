import json
from pathlib import Path


class UserJsonRepository:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def find_by_email(self, email: str):
        users = self._load_users()
        return next((u for u in users if u["email"] == email), None)

    def find_by_id(self, user_id: int):
        users = self._load_users()
        return next((u for u in users if u["id"] == user_id), None)

    def list_all(self) -> list:
        return self._load_users()

    def save(self, user: dict):
        users = self._load_users()
        users.append(user)
        self._save_users(users)

    def delete_by_id(self, user_id: int) -> bool:
        users = self._load_users()
        updated = [u for u in users if u["id"] != user_id]
        if len(updated) == len(users):
            return False
        self._save_users(updated)
        return True

    def _load_users(self):
        if not self.file_path.exists():
            return []

        content = self.file_path.read_text(encoding="utf-8")

        if not content.strip():
            return []

        return json.loads(content)

    def _save_users(self, users: list):
        self.file_path.write_text(
            json.dumps(users, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
