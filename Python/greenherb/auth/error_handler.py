from greenherb.auth.exceptions import (
    InvalidCredentials,
    InvalidToken,
    TokenExpired,
    AccessDenied,
    ValidationError,
)


def handle_auth_error(error: Exception) -> dict:
    if isinstance(error, ValidationError):
        return {
            "status_code": 400,
            "body": {
                "error": "VALIDATION_ERROR",
                "message": "Pedido inválido"
            }
        }

    if isinstance(error, InvalidCredentials):
        return {
            "status_code": 401,
            "body": {
                "error": "INVALID_CREDENTIALS",
                "message": "Credenciais inválidas"
            }
        }

    if isinstance(error, TokenExpired):
        return {
            "status_code": 401,
            "body": {
                "error": "TOKEN_EXPIRED",
                "message": "Token expirado"
            }
        }

    if isinstance(error, InvalidToken):
        return {
            "status_code": 401,
            "body": {
                "error": "INVALID_TOKEN",
                "message": "Token inválido"
            }
        }

    if isinstance(error, AccessDenied):
        return {
            "status_code": 403,
            "body": {
                "error": "ACCESS_DENIED",
                "message": "Permissão negada"
            }
        }

    return {
        "status_code": 500,
        "body": {
            "error": "INTERNAL_ERROR",
            "message": "Erro interno"
        }
    }
