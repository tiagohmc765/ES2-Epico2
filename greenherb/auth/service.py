from greenherb.auth.exceptions import InvalidCredentials, InvalidToken


class AuthService:
    def __init__(self, user_repository, password_hasher, jwt_provider):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.jwt_provider = jwt_provider

    def login(self, email: str, password: str) -> dict:
        user = self.user_repository.find_by_email(email)

        if user is None:
            raise InvalidCredentials("Credenciais inválidas")

        if not self.password_hasher.verify(password, user["password_hash"]):
            raise InvalidCredentials("Credenciais inválidas")

        return {
            "access_token": self.jwt_provider.create_access_token(user),
            "refresh_token": self.jwt_provider.create_refresh_token(user)
        }

    def refresh_access_token(self, refresh_token: str) -> dict:
        payload = self.jwt_provider.decode(refresh_token)

        if payload["type"] != "refresh":
            raise InvalidToken("Token não é refresh token")

        user = self.user_repository.find_by_id(payload["sub"])

        if user is None:
            raise InvalidToken("Utilizador inexistente")

        return {
            "access_token": self.jwt_provider.create_access_token(user)
        }
