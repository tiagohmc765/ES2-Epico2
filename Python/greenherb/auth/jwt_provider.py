import base64
import hashlib
import hmac
import json
import time

from greenherb.auth.exceptions import InvalidToken, TokenExpired


class JwtProvider:
    def __init__(self, secret: str, access_token_ttl: int = 900, refresh_token_ttl: int = 3600):
        self.secret = secret
        self.access_token_ttl = access_token_ttl
        self.refresh_token_ttl = refresh_token_ttl

    def create_access_token(self, user: dict) -> str:
        return self._create_token(user, self.access_token_ttl, "access")

    def create_refresh_token(self, user: dict) -> str:
        return self._create_token(user, self.refresh_token_ttl, "refresh")

    def decode(self, token: str) -> dict:
        try:
            payload_encoded, signature = token.split(".")
        except ValueError:
            raise InvalidToken("Token malformado")

        expected_signature = self._sign(payload_encoded)

        if not hmac.compare_digest(signature, expected_signature):
            raise InvalidToken("Assinatura inválida")

        payload_json = base64.urlsafe_b64decode(payload_encoded.encode()).decode()
        payload = json.loads(payload_json)

        if payload["exp"] < int(time.time()):
            raise TokenExpired("Token expirado")

        return payload

    def _create_token(self, user: dict, ttl: int, token_type: str) -> str:
        payload = {
            "sub": user["id"],
            "email": user["email"],
            "role": user["role"],
            "type": token_type,
            "exp": int(time.time()) + ttl
        }

        payload_json = json.dumps(payload, separators=(",", ":"))
        payload_encoded = base64.urlsafe_b64encode(payload_json.encode()).decode()
        signature = self._sign(payload_encoded)

        return f"{payload_encoded}.{signature}"

    def _sign(self, payload_encoded: str) -> str:
        return hmac.new(
            self.secret.encode(),
            payload_encoded.encode(),
            hashlib.sha256
        ).hexdigest()
