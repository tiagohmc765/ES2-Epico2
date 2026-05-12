import hashlib


class PasswordHasher:
    def hash(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def verify(self, password: str, password_hash: str) -> bool:
        return self.hash(password) == password_hash
