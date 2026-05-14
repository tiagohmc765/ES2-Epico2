import pytest
import time

from greenherb.auth.jwt_provider import JwtProvider
from greenherb.auth.exceptions import InvalidToken, TokenExpired


def test_tu_jwt_01_create_access_token_e_decode_devolve_payload():
    provider = JwtProvider(secret="segredo")

    user = {
        "id": 1,
        "email": "admin@greenherb.pt",
        "role": "ADMIN"
    }

    token = provider.create_access_token(user)
    payload = provider.decode(token)

    assert payload["sub"] == 1
    assert payload["email"] == "admin@greenherb.pt"
    assert payload["role"] == "ADMIN"
    assert payload["type"] == "access"


def test_tu_jwt_02_create_refresh_token_e_decode_devolve_payload():
    provider = JwtProvider(secret="segredo")

    user = {
        "id": 1,
        "email": "admin@greenherb.pt",
        "role": "ADMIN"
    }

    token = provider.create_refresh_token(user)
    payload = provider.decode(token)

    assert payload["sub"] == 1
    assert payload["type"] == "refresh"


def test_tu_jwt_03_decode_rejeita_token_malformado():
    provider = JwtProvider(secret="segredo")

    with pytest.raises(InvalidToken):
        provider.decode("token-invalido")


def test_tu_jwt_04_decode_rejeita_token_com_assinatura_invalida():
    provider = JwtProvider(secret="segredo")

    user = {
        "id": 1,
        "email": "admin@greenherb.pt",
        "role": "ADMIN"
    }

    token = provider.create_access_token(user)
    payload, _signature = token.split(".")
    token_adulterado = f"{payload}.assinatura_invalida"

    with pytest.raises(InvalidToken):
        provider.decode(token_adulterado)


def test_tu_jwt_05_decode_rejeita_token_expirado():
    provider = JwtProvider(secret="segredo", access_token_ttl=-1)

    user = {
        "id": 1,
        "email": "admin@greenherb.pt",
        "role": "ADMIN"
    }

    token = provider.create_access_token(user)

    time.sleep(1)

    with pytest.raises(TokenExpired):
        provider.decode(token)


# ---------------------------------------------------------------------------
# Análise de Valores Limite — TTL do token
# Intervalo aceitável definido: [1, 86400] segundos
# Valores testados: -1 (abaixo do mínimo), 1 (limite inferior),
#                   900 (valor nominal), 86400 (limite superior), 86401 (acima do máximo)
# ---------------------------------------------------------------------------

def test_tu_jwt_vl_01_ttl_abaixo_do_minimo_token_expira_imediatamente():
    """VL: TTL = -1 — abaixo do limite inferior; token deve ser rejeitado."""
    provider = JwtProvider(secret="segredo", access_token_ttl=-1)
    user = {"id": 1, "email": "admin@greenherb.pt", "role": "ADMIN"}

    token = provider.create_access_token(user)
    time.sleep(1)

    with pytest.raises(TokenExpired):
        provider.decode(token)


def test_tu_jwt_vl_02_ttl_limite_inferior_token_e_valido():
    """VL: TTL = 1 — limite inferior válido; token criado e decodificado com sucesso."""
    provider = JwtProvider(secret="segredo", access_token_ttl=1)
    user = {"id": 1, "email": "admin@greenherb.pt", "role": "ADMIN"}

    token = provider.create_access_token(user)
    payload = provider.decode(token)

    assert payload["sub"] == 1
    assert payload["type"] == "access"


def test_tu_jwt_vl_03_ttl_valor_nominal_token_e_valido():
    """VL: TTL = 900 — valor nominal (15 minutos); token válido."""
    provider = JwtProvider(secret="segredo", access_token_ttl=900)
    user = {"id": 1, "email": "admin@greenherb.pt", "role": "ADMIN"}

    token = provider.create_access_token(user)
    payload = provider.decode(token)

    assert payload["sub"] == 1


def test_tu_jwt_vl_04_ttl_limite_superior_token_e_valido():
    """VL: TTL = 86400 — limite superior (1 dia); token válido."""
    provider = JwtProvider(secret="segredo", access_token_ttl=86400)
    user = {"id": 1, "email": "admin@greenherb.pt", "role": "ADMIN"}

    token = provider.create_access_token(user)
    payload = provider.decode(token)

    assert payload["sub"] == 1


def test_tu_jwt_vl_05_ttl_acima_do_maximo_token_e_valido():
    """VL: TTL = 86401 — acima do limite superior; o sistema aceita mas ultrapassa a política."""
    provider = JwtProvider(secret="segredo", access_token_ttl=86401)
    user = {"id": 1, "email": "admin@greenherb.pt", "role": "ADMIN"}

    token = provider.create_access_token(user)
    payload = provider.decode(token)

    assert payload["sub"] == 1
