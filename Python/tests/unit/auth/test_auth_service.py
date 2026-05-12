from unittest.mock import Mock

import pytest

from greenherb.auth.service import AuthService
from greenherb.auth.exceptions import InvalidCredentials, InvalidToken


def test_tu_auth_04_login_com_credenciais_validas_devolve_tokens():
    repository = Mock()
    hasher = Mock()
    jwt_provider = Mock()

    user = {
        "id": 1,
        "email": "admin@greenherb.pt",
        "password_hash": "hash",
        "role": "ADMIN"
    }

    repository.find_by_email.return_value = user
    hasher.verify.return_value = True
    jwt_provider.create_access_token.return_value = "access-token"
    jwt_provider.create_refresh_token.return_value = "refresh-token"

    service = AuthService(repository, hasher, jwt_provider)

    result = service.login("admin@greenherb.pt", "Admin123!")

    assert result["access_token"] == "access-token"
    assert result["refresh_token"] == "refresh-token"


def test_tu_auth_05_login_com_password_errada_lanca_invalid_credentials():
    repository = Mock()
    hasher = Mock()
    jwt_provider = Mock()

    repository.find_by_email.return_value = {
        "id": 1,
        "email": "admin@greenherb.pt",
        "password_hash": "hash",
        "role": "ADMIN"
    }

    hasher.verify.return_value = False

    service = AuthService(repository, hasher, jwt_provider)

    with pytest.raises(InvalidCredentials):
        service.login("admin@greenherb.pt", "Errada123!")


def test_tu_auth_06_login_com_utilizador_inexistente_lanca_invalid_credentials():
    repository = Mock()
    hasher = Mock()
    jwt_provider = Mock()

    repository.find_by_email.return_value = None

    service = AuthService(repository, hasher, jwt_provider)

    with pytest.raises(InvalidCredentials):
        service.login("naoexiste@greenherb.pt", "Admin123!")


def test_tu_auth_07_refresh_token_valido_devolve_novo_access_token():
    repository = Mock()
    hasher = Mock()
    jwt_provider = Mock()

    jwt_provider.decode.return_value = {
        "sub": 1,
        "email": "admin@greenherb.pt",
        "role": "ADMIN",
        "type": "refresh"
    }

    repository.find_by_id.return_value = {
        "id": 1,
        "email": "admin@greenherb.pt",
        "password_hash": "hash",
        "role": "ADMIN"
    }

    jwt_provider.create_access_token.return_value = "novo-access-token"

    service = AuthService(repository, hasher, jwt_provider)

    result = service.refresh_access_token("refresh-token")

    assert result["access_token"] == "novo-access-token"


def test_tu_auth_08_refresh_com_access_token_lanca_invalid_token():
    repository = Mock()
    hasher = Mock()
    jwt_provider = Mock()

    jwt_provider.decode.return_value = {
        "sub": 1,
        "email": "admin@greenherb.pt",
        "role": "ADMIN",
        "type": "access"
    }

    service = AuthService(repository, hasher, jwt_provider)

    with pytest.raises(InvalidToken):
        service.refresh_access_token("access-token")


def test_tu_auth_09_refresh_com_utilizador_inexistente_lanca_invalid_token():
    repository = Mock()
    hasher = Mock()
    jwt_provider = Mock()

    jwt_provider.decode.return_value = {
        "sub": 999,
        "email": "ghost@greenherb.pt",
        "role": "ADMIN",
        "type": "refresh"
    }

    repository.find_by_id.return_value = None

    service = AuthService(repository, hasher, jwt_provider)

    with pytest.raises(InvalidToken):
        service.refresh_access_token("refresh-token")
