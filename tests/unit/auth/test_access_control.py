import pytest

from greenherb.auth.access_control import require_role
from greenherb.auth.exceptions import AccessDenied


def test_tu_auth_10_admin_tem_acesso_a_recurso_de_admin():
    user = {
        "id": 1,
        "email": "admin@greenherb.pt",
        "role": "ADMIN"
    }

    assert require_role(user, ["ADMIN"]) is True


def test_tu_auth_11_tecnico_nao_tem_acesso_a_recurso_de_admin():
    user = {
        "id": 2,
        "email": "tecnico@greenherb.pt",
        "role": "TECNICO"
    }

    with pytest.raises(AccessDenied):
        require_role(user, ["ADMIN"])


def test_tu_auth_12_sem_utilizador_lanca_access_denied():
    with pytest.raises(AccessDenied):
        require_role(None, ["ADMIN"])


def test_tu_auth_13_responsavel_tem_acesso_a_recurso_de_responsavel_ou_admin():
    user = {
        "id": 3,
        "email": "responsavel@greenherb.pt",
        "role": "RESPONSAVEL"
    }

    assert require_role(user, ["RESPONSAVEL", "ADMIN"]) is True
