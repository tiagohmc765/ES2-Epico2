from greenherb.auth.error_handler import handle_auth_error
from greenherb.auth.exceptions import (
    InvalidCredentials,
    InvalidToken,
    TokenExpired,
    AccessDenied,
    ValidationError,
)


def test_tu_error_01_validation_error_devolve_400_json():
    response = handle_auth_error(ValidationError())

    assert response["status_code"] == 400
    assert response["body"]["error"] == "VALIDATION_ERROR"


def test_tu_error_02_invalid_credentials_devolve_401_json():
    response = handle_auth_error(InvalidCredentials())

    assert response["status_code"] == 401
    assert response["body"]["error"] == "INVALID_CREDENTIALS"


def test_tu_error_03_token_expired_devolve_401_json():
    response = handle_auth_error(TokenExpired())

    assert response["status_code"] == 401
    assert response["body"]["error"] == "TOKEN_EXPIRED"


def test_tu_error_04_invalid_token_devolve_401_json():
    response = handle_auth_error(InvalidToken())

    assert response["status_code"] == 401
    assert response["body"]["error"] == "INVALID_TOKEN"


def test_tu_error_05_access_denied_devolve_403_json():
    response = handle_auth_error(AccessDenied())

    assert response["status_code"] == 403
    assert response["body"]["error"] == "ACCESS_DENIED"


def test_tu_error_06_erro_desconhecido_devolve_500_json():
    response = handle_auth_error(Exception())

    assert response["status_code"] == 500
    assert response["body"]["error"] == "INTERNAL_ERROR"
