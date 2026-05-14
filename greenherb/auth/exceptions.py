class AuthError(Exception):
    pass


class InvalidCredentials(AuthError):
    pass


class TokenExpired(AuthError):
    pass


class InvalidToken(AuthError):
    pass


class AccessDenied(AuthError):
    pass


class ValidationError(AuthError):
    pass
