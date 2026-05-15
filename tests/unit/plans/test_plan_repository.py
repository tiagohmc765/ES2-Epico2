import json
import pytest

from greenherb.plans.repository import PlanJsonRepository

# ===========================================================================
# PARTICIONAMENTO DE EQUIVALÊNCIA — PlanJsonRepository
#
# Domínio: operações sobre ficheiro JSON de planos de cultivo
#
# _load / list_all:
#   EC-PREPO-FILE-I1  Ficheiro JSON inexistente → lista vazia (sem erro)
#   EC-PREPO-FILE-I2  Ficheiro JSON existe mas está vazio → lista vazia
#   EC-PREPO-FILE-V1  Ficheiro JSON com planos → lista com os objetos
#
# find_by_id(plan_id):
#   EC-PREPO-FIND-V1   id existente → devolve dict do plano
#   EC-PREPO-FIND-I1   id inexistente → devolve None
#
# save(plan):
#   EC-PREPO-SAVE-V1   repositório com planos → id incrementado e plano persistido
#   EC-PREPO-SAVE-V2   repositório vazio → id=1 atribuído (caso limite)
# ===========================================================================

VALID_PLAN = {
    "type": "regular",
    "temp_min": 18.0,
    "temp_max": 28.0,
    "humidity_min": 40.0,
    "humidity_max": 80.0,
    "luminosity_min": 5000.0,
    "luminosity_max": 25000.0,
    "cycle_days": 90,
    "authorized_by": None,
}


@pytest.fixture
def repo(tmp_path):
    return PlanJsonRepository(str(tmp_path / "plans.json"))


@pytest.fixture
def repo_com_dados(tmp_path):
    path = tmp_path / "plans.json"
    data = [
        {**VALID_PLAN, "id": 1, "type": "regular"},
        {**VALID_PLAN, "id": 2, "type": "emergencia"},
    ]
    path.write_text(json.dumps(data), encoding="utf-8")
    return PlanJsonRepository(str(path))


# ---------------------------------------------------------------------------
# _load / list_all
# ---------------------------------------------------------------------------

def test_tu_plan_repo_01_list_all_com_ficheiro_inexistente_devolve_lista_vazia(repo):
    """EC-PREPO-FILE-I1 — Ficheiro JSON não existe → list_all devolve []."""
    result = repo.list_all()
    assert result == []


def test_tu_plan_repo_02_list_all_com_ficheiro_vazio_devolve_lista_vazia(tmp_path):
    """EC-PREPO-FILE-I2 — Ficheiro JSON existe mas está vazio → list_all devolve []."""
    path = tmp_path / "plans.json"
    path.write_text("", encoding="utf-8")
    r = PlanJsonRepository(str(path))
    assert r.list_all() == []


def test_tu_plan_repo_03_list_all_com_ficheiro_com_dados_devolve_lista(repo_com_dados):
    """EC-PREPO-FILE-V1 — Ficheiro JSON com planos → list_all devolve lista com todos."""
    result = repo_com_dados.list_all()
    assert len(result) == 2
    assert result[0]["type"] == "regular"
    assert result[1]["type"] == "emergencia"


# ---------------------------------------------------------------------------
# find_by_id
# ---------------------------------------------------------------------------

def test_tu_plan_repo_04_find_by_id_com_id_existente_devolve_plano(repo_com_dados):
    """EC-PREPO-FIND-V1 — id existente no ficheiro → devolve dict do plano."""
    result = repo_com_dados.find_by_id(1)
    assert result is not None
    assert result["type"] == "regular"


def test_tu_plan_repo_05_find_by_id_com_id_inexistente_devolve_none(repo_com_dados):
    """EC-PREPO-FIND-I1 — id inexistente no ficheiro → devolve None."""
    result = repo_com_dados.find_by_id(999)
    assert result is None


# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------

def test_tu_plan_repo_06_save_em_repositorio_vazio_atribui_id_1(repo):
    """EC-PREPO-SAVE-V2 — repositório vazio: primeiro plano salvo recebe id=1 (caso limite)."""
    result = repo.save(VALID_PLAN.copy())
    assert result["id"] == 1


def test_tu_plan_repo_07_save_em_repositorio_com_planos_atribui_id_sequencial(repo_com_dados):
    """EC-PREPO-SAVE-V1 — repositório com 2 planos: próximo recebe id=3."""
    result = repo_com_dados.save(VALID_PLAN.copy())
    assert result["id"] == 3


def test_tu_plan_repo_08_save_persiste_plano_em_disco(repo):
    """EC-PREPO-SAVE-V1 — save persiste: list_all após save devolve o plano guardado."""
    repo.save({**VALID_PLAN, "type": "emergencia"})
    plans = repo.list_all()
    assert len(plans) == 1
    assert plans[0]["type"] == "emergencia"
