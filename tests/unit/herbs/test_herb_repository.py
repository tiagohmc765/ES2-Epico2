import json
import pytest

from greenherb.herbs.repository import HerbJsonRepository

# ===========================================================================
# PARTICIONAMENTO DE EQUIVALÊNCIA — HerbJsonRepository
#
# Domínio: operações sobre ficheiro JSON de ervas
#
# _load / list_all:
#   EC-REPO-FILE-I1  Ficheiro JSON inexistente → lista vazia (sem erro)
#   EC-REPO-FILE-I2  Ficheiro JSON existe mas está vazio → lista vazia
#   EC-REPO-FILE-V1  Ficheiro JSON com ervas → lista com os objetos
#
# find_by_id(herb_id):
#   EC-REPO-FIND-V1   id existente → devolve dict da erva
#   EC-REPO-FIND-I1   id inexistente → devolve None
#
# find_by_name(name):
#   EC-REPO-NAME-V1   nome existente (case-insensitive) → devolve dict da erva
#   EC-REPO-NAME-I1   nome inexistente → devolve None
#
# save(herb):
#   EC-REPO-SAVE-V1   repositório com ervas → id incrementado e erva persistida
#   EC-REPO-SAVE-V2   repositório vazio → id=1 atribuído (caso limite)
#
# save_many(herb_list):
#   EC-REPO-MANY-V1   lista com ervas → ids sequenciais, todas persistidas
#   EC-REPO-MANY-V2   lista vazia → repositório inalterado (caso limite)
# ===========================================================================


@pytest.fixture
def repo(tmp_path):
    return HerbJsonRepository(str(tmp_path / "herbs.json"))


@pytest.fixture
def repo_com_dados(tmp_path):
    path = tmp_path / "herbs.json"
    data = [
        {"id": 1, "name": "Basil", "family": "Lamiaceae"},
        {"id": 2, "name": "Rosemary", "family": "Lamiaceae"},
    ]
    path.write_text(json.dumps(data), encoding="utf-8")
    return HerbJsonRepository(str(path))


# ---------------------------------------------------------------------------
# _load / list_all
# ---------------------------------------------------------------------------

def test_tu_herb_repo_01_list_all_com_ficheiro_inexistente_devolve_lista_vazia(repo):
    """EC-REPO-FILE-I1 — Ficheiro JSON não existe → list_all devolve []."""
    result = repo.list_all()
    assert result == []


def test_tu_herb_repo_02_list_all_com_ficheiro_vazio_devolve_lista_vazia(tmp_path):
    """EC-REPO-FILE-I2 — Ficheiro JSON existe mas está vazio → list_all devolve []."""
    path = tmp_path / "herbs.json"
    path.write_text("", encoding="utf-8")
    r = HerbJsonRepository(str(path))
    assert r.list_all() == []


def test_tu_herb_repo_03_list_all_com_ficheiro_com_dados_devolve_lista(repo_com_dados):
    """EC-REPO-FILE-V1 — Ficheiro JSON com ervas → list_all devolve lista com todas."""
    result = repo_com_dados.list_all()
    assert len(result) == 2
    assert result[0]["name"] == "Basil"
    assert result[1]["name"] == "Rosemary"


# ---------------------------------------------------------------------------
# find_by_id
# ---------------------------------------------------------------------------

def test_tu_herb_repo_04_find_by_id_com_id_existente_devolve_erva(repo_com_dados):
    """EC-REPO-FIND-V1 — id existente no ficheiro → devolve dict da erva."""
    result = repo_com_dados.find_by_id(1)
    assert result is not None
    assert result["name"] == "Basil"


def test_tu_herb_repo_05_find_by_id_com_id_inexistente_devolve_none(repo_com_dados):
    """EC-REPO-FIND-I1 — id inexistente no ficheiro → devolve None."""
    result = repo_com_dados.find_by_id(999)
    assert result is None


# ---------------------------------------------------------------------------
# find_by_name
# ---------------------------------------------------------------------------

def test_tu_herb_repo_06_find_by_name_com_nome_existente_devolve_erva(repo_com_dados):
    """EC-REPO-NAME-V1 — nome existente → devolve dict da erva."""
    result = repo_com_dados.find_by_name("Basil")
    assert result is not None
    assert result["id"] == 1


def test_tu_herb_repo_07_find_by_name_com_nome_inexistente_devolve_none(repo_com_dados):
    """EC-REPO-NAME-I1 — nome não registado → devolve None."""
    result = repo_com_dados.find_by_name("Mint")
    assert result is None


def test_tu_herb_repo_08_find_by_name_e_case_insensitive(repo_com_dados):
    """EC-REPO-NAME-V1 — nome em diferentes capitalizações → encontrado (case-insensitive)."""
    assert repo_com_dados.find_by_name("basil") is not None
    assert repo_com_dados.find_by_name("BASIL") is not None
    assert repo_com_dados.find_by_name("BaSiL") is not None


# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------

def test_tu_herb_repo_09_save_em_repositorio_vazio_atribui_id_1(repo):
    """EC-REPO-SAVE-V2 — repositório vazio: primeira erva salva recebe id=1 (caso limite)."""
    result = repo.save({"name": "Mint", "family": "Lamiaceae"})
    assert result["id"] == 1


def test_tu_herb_repo_10_save_em_repositorio_com_ervas_atribui_id_sequencial(repo_com_dados):
    """EC-REPO-SAVE-V1 — repositório com 2 ervas: próxima recebe id=3."""
    result = repo_com_dados.save({"name": "Mint", "family": "Lamiaceae"})
    assert result["id"] == 3


def test_tu_herb_repo_11_save_persiste_erva_em_disco(repo):
    """EC-REPO-SAVE-V1 — save persiste: list_all após save devolve a erva guardada."""
    repo.save({"name": "Mint", "family": "Lamiaceae"})
    herbs = repo.list_all()
    assert len(herbs) == 1
    assert herbs[0]["name"] == "Mint"


# ---------------------------------------------------------------------------
# save_many
# ---------------------------------------------------------------------------

def test_tu_herb_repo_12_save_many_atribui_ids_sequenciais_e_persiste_todas(repo):
    """EC-REPO-MANY-V1 — save_many com lista de 3 ervas: ids 1, 2, 3 atribuídos e persistidos."""
    herbs = [
        {"name": "Basil", "family": "Lamiaceae"},
        {"name": "Rosemary", "family": "Lamiaceae"},
        {"name": "Mint", "family": "Lamiaceae"},
    ]
    saved = repo.save_many(herbs)

    assert [h["id"] for h in saved] == [1, 2, 3]
    assert len(repo.list_all()) == 3


def test_tu_herb_repo_13_save_many_com_lista_vazia_nao_altera_repositorio(repo):
    """EC-REPO-MANY-V2 — save_many com lista vazia: repositório permanece inalterado (caso limite)."""
    saved = repo.save_many([])
    assert saved == []
    assert repo.list_all() == []
