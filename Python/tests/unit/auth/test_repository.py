import json

from greenherb.auth.repository import UserJsonRepository


def test_tu_repo_01_find_by_email_devolve_utilizador_existente(tmp_path):
    file_path = tmp_path / "users.json"

    file_path.write_text(json.dumps([
        {
            "id": 1,
            "email": "admin@greenherb.pt",
            "password_hash": "hash",
            "role": "ADMIN"
        }
    ]), encoding="utf-8")

    repository = UserJsonRepository(str(file_path))

    user = repository.find_by_email("admin@greenherb.pt")

    assert user["id"] == 1
    assert user["role"] == "ADMIN"


def test_tu_repo_02_find_by_email_devolve_none_quando_utilizador_nao_existe(tmp_path):
    file_path = tmp_path / "users.json"
    file_path.write_text("[]", encoding="utf-8")

    repository = UserJsonRepository(str(file_path))

    user = repository.find_by_email("naoexiste@greenherb.pt")

    assert user is None


def test_tu_repo_03_find_by_id_devolve_utilizador_existente(tmp_path):
    file_path = tmp_path / "users.json"

    file_path.write_text(json.dumps([
        {
            "id": 1,
            "email": "admin@greenherb.pt",
            "password_hash": "hash",
            "role": "ADMIN"
        }
    ]), encoding="utf-8")

    repository = UserJsonRepository(str(file_path))

    user = repository.find_by_id(1)

    assert user["email"] == "admin@greenherb.pt"


def test_tu_repo_04_find_by_id_devolve_none_quando_utilizador_nao_existe(tmp_path):
    file_path = tmp_path / "users.json"
    file_path.write_text("[]", encoding="utf-8")

    repository = UserJsonRepository(str(file_path))

    user = repository.find_by_id(999)

    assert user is None


def test_tu_repo_05_save_persiste_utilizador_em_json(tmp_path):
    file_path = tmp_path / "users.json"
    file_path.write_text("[]", encoding="utf-8")

    repository = UserJsonRepository(str(file_path))

    repository.save({
        "id": 1,
        "email": "admin@greenherb.pt",
        "password_hash": "hash",
        "role": "ADMIN"
    })

    users = json.loads(file_path.read_text(encoding="utf-8"))

    assert len(users) == 1
    assert users[0]["email"] == "admin@greenherb.pt"


def test_tu_repo_06_load_users_devolve_lista_vazia_se_ficheiro_nao_existe(tmp_path):
    file_path = tmp_path / "missing.json"

    repository = UserJsonRepository(str(file_path))

    assert repository._load_users() == []


def test_tu_repo_07_load_users_devolve_lista_vazia_se_ficheiro_vazio(tmp_path):
    file_path = tmp_path / "users.json"
    file_path.write_text("", encoding="utf-8")

    repository = UserJsonRepository(str(file_path))

    assert repository._load_users() == []
