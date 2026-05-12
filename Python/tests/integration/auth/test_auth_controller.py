import json

import pytest
from fastapi.testclient import TestClient

from greenherb.app import app
from greenherb.auth import controller, users_controller
from greenherb.auth.password_hasher import PasswordHasher

_hasher = PasswordHasher()


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_users = [
        {
            "id": 1,
            "email": "admin@test.pt",
            "password_hash": _hasher.hash("Admin123!"),
            "role": "ADMIN",
        },
        {
            "id": 2,
            "email": "tecnico@test.pt",
            "password_hash": _hasher.hash("Tecnico123!"),
            "role": "TECNICO",
        },
    ]
    test_file = tmp_path / "users.json"
    test_file.write_text(json.dumps(test_users), encoding="utf-8")

    monkeypatch.setattr(controller.repository, "file_path", test_file)
    monkeypatch.setattr(users_controller.repository, "file_path", test_file)

    return TestClient(app)


@pytest.fixture
def admin_token(client):
    response = client.post("/auth/login", json={"email": "admin@test.pt", "password": "Admin123!"})
    return response.json()["access_token"]


@pytest.fixture
def tecnico_token(client):
    response = client.post("/auth/login", json={"email": "tecnico@test.pt", "password": "Tecnico123!"})
    return response.json()["access_token"]


# ---------------------------------------------------------------------------
# POST /auth/login — Particionamento de Equivalência
# ---------------------------------------------------------------------------

def test_ti_auth_01_login_com_credenciais_validas_devolve_200_e_tokens(client):
    response = client.post("/auth/login", json={"email": "admin@test.pt", "password": "Admin123!"})

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body


def test_ti_auth_02_login_com_password_errada_devolve_401(client):
    response = client.post("/auth/login", json={"email": "admin@test.pt", "password": "Errada123!"})

    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "INVALID_CREDENTIALS"


def test_ti_auth_03_login_com_utilizador_inexistente_devolve_401(client):
    response = client.post("/auth/login", json={"email": "naoexiste@test.pt", "password": "Admin123!"})

    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "INVALID_CREDENTIALS"


def test_ti_auth_04_login_sem_campo_password_devolve_400(client):
    response = client.post("/auth/login", json={"email": "admin@test.pt"})

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "VALIDATION_ERROR"


def test_ti_auth_04b_login_sem_campo_email_devolve_400(client):
    response = client.post("/auth/login", json={"password": "Admin123!"})

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "VALIDATION_ERROR"


# ---------------------------------------------------------------------------
# POST /auth/refresh — Particionamento de Equivalência
# ---------------------------------------------------------------------------

def test_ti_auth_05_refresh_com_token_valido_devolve_200_e_access_token(client):
    login = client.post("/auth/login", json={"email": "admin@test.pt", "password": "Admin123!"})
    refresh_token = login.json()["refresh_token"]

    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_ti_auth_06_refresh_com_access_token_devolve_401(client):
    login = client.post("/auth/login", json={"email": "admin@test.pt", "password": "Admin123!"})
    access_token = login.json()["access_token"]

    response = client.post("/auth/refresh", json={"refresh_token": access_token})

    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "INVALID_TOKEN"


def test_ti_auth_07_refresh_sem_campo_devolve_400(client):
    response = client.post("/auth/refresh", json={})

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "VALIDATION_ERROR"


# ---------------------------------------------------------------------------
# GET /users — Controlo de acesso por perfil (Particionamento de Equivalência)
# ---------------------------------------------------------------------------

def test_ti_users_01_admin_lista_utilizadores_devolve_200(client, admin_token):
    response = client.get("/users", headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) == 2


def test_ti_users_02_tecnico_nao_pode_listar_utilizadores_devolve_403(client, tecnico_token):
    response = client.get("/users", headers={"Authorization": f"Bearer {tecnico_token}"})

    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "ACCESS_DENIED"


def test_ti_users_03_sem_token_devolve_403(client):
    response = client.get("/users")

    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "ACCESS_DENIED"


# ---------------------------------------------------------------------------
# POST /users — Criação de utilizador (Particionamento de Equivalência)
# ---------------------------------------------------------------------------

def test_ti_users_04_admin_cria_utilizador_valido_devolve_201(client, admin_token):
    response = client.post(
        "/users",
        json={"email": "novo@test.pt", "password": "Novo123!", "role": "TECNICO"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "novo@test.pt"
    assert body["role"] == "TECNICO"
    assert "password" not in body
    assert "password_hash" not in body


def test_ti_users_05_admin_cria_utilizador_com_role_invalido_devolve_400(client, admin_token):
    response = client.post(
        "/users",
        json={"email": "novo2@test.pt", "password": "Novo123!", "role": "SUPERADMIN"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "VALIDATION_ERROR"


def test_ti_users_05b_admin_cria_utilizador_sem_campos_obrigatorios_devolve_400(client, admin_token):
    response = client.post(
        "/users",
        json={"email": "novo2@test.pt"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "VALIDATION_ERROR"


def test_ti_users_06_admin_cria_utilizador_email_duplicado_devolve_400(client, admin_token):
    response = client.post(
        "/users",
        json={"email": "admin@test.pt", "password": "Admin123!", "role": "ADMIN"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "VALIDATION_ERROR"


def test_ti_users_07_tecnico_nao_pode_criar_utilizador_devolve_403(client, tecnico_token):
    response = client.post(
        "/users",
        json={"email": "novo3@test.pt", "password": "Novo123!", "role": "TECNICO"},
        headers={"Authorization": f"Bearer {tecnico_token}"},
    )

    assert response.status_code == 403


# ---------------------------------------------------------------------------
# GET /users/{id} e DELETE /users/{id}
# ---------------------------------------------------------------------------

def test_ti_users_08_admin_obtem_utilizador_existente_devolve_200(client, admin_token):
    response = client.get("/users/1", headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_ti_users_09_admin_obtem_utilizador_inexistente_devolve_404(client, admin_token):
    response = client.get("/users/999", headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 404


def test_ti_users_10_admin_elimina_utilizador_existente_devolve_204(client, admin_token):
    response = client.delete("/users/2", headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 204


def test_ti_users_11_admin_elimina_utilizador_inexistente_devolve_404(client, admin_token):
    response = client.delete("/users/999", headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Token inválido em endpoints de /users — cobrir ramos AuthError
# ---------------------------------------------------------------------------

def test_ti_users_12_token_invalido_em_list_devolve_401(client):
    response = client.get("/users", headers={"Authorization": "Bearer token-invalido"})

    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "INVALID_TOKEN"


def test_ti_users_13_token_invalido_em_get_user_devolve_401(client):
    response = client.get("/users/1", headers={"Authorization": "Bearer token-invalido"})

    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "INVALID_TOKEN"


def test_ti_users_14_token_invalido_em_delete_user_devolve_401(client):
    response = client.delete("/users/1", headers={"Authorization": "Bearer token-invalido"})

    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "INVALID_TOKEN"
