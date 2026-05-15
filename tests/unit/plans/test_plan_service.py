import pytest
from unittest.mock import MagicMock

from greenherb.plans.service import PlanService
from greenherb.plans.exceptions import PlanNotFound, PlanValidationError, UnauthorizedPontualPlan

# ===========================================================================
# PARTICIONAMENTO DE EQUIVALÊNCIA — PlanService
#
# Domínio: métodos list_plans, get_plan, create_plan
#
# list_plans:
#   EC-PSVC-LIST-V1  Repositório com planos → lista devolvida
#   EC-PSVC-LIST-V2  Repositório vazio → lista vazia (caso limite)
#
# get_plan(plan_id):
#   EC-PSVC-GET-V1   id existente → plano devolvido
#   EC-PSVC-GET-I1   id inexistente → lança PlanNotFound
#
# create_plan(data, authorized_by):
#   EC-PSVC-CREATE-V1  Dados válidos (regular/emergencia) → plano validado e guardado
#   EC-PSVC-CREATE-I1  Dados inválidos (parâmetros fora do intervalo) → PlanValidationError propagada
#   EC-PSVC-CREATE-V2  Plano pontual com authorized_by presente → plano criado
#   EC-PSVC-CREATE-I2  Plano pontual sem authorized_by → UnauthorizedPontualPlan propagada
#
# ===========================================================================
# MC/DC — create_plan (decisão em validate_plan, exercida ao nível do serviço)
#
# Decisão: if type == "pontual" AND authorized_by is None → rejeitar
# C1 = type == "pontual"
# C2 = authorized_by is not None
#
#   MC/DC C1=F, C2=F → regular sem auth → aceite      (test_11, EC-PSVC-CREATE-V1)
#   MC/DC C1=T, C2=F → pontual sem auth → rejeitar    (test_09, EC-PSVC-CREATE-I2)
#   MC/DC C1=T, C2=T → pontual com auth → aceite      (test_08, EC-PSVC-CREATE-V2)
#   MC/DC C1=F, C2=T → regular com auth → aceite      (test_10, EC-PSVC-CREATE-V1)
# ===========================================================================

VALID_PLAN_DATA = {
    "type": "regular",
    "temp_min": 18.0,
    "temp_max": 28.0,
    "humidity_min": 40.0,
    "humidity_max": 80.0,
    "luminosity_min": 5000.0,
    "luminosity_max": 25000.0,
    "cycle_days": 90,
}


@pytest.fixture
def repo():
    return MagicMock()


@pytest.fixture
def service(repo):
    return PlanService(repository=repo)


# ---------------------------------------------------------------------------
# list_plans
# ---------------------------------------------------------------------------

def test_tu_plan_service_01_list_plans_com_planos_devolve_lista(service, repo):
    """EC-PSVC-LIST-V1 — Repositório com planos → lista completa devolvida."""
    repo.list_all.return_value = [
        {"id": 1, "type": "regular"},
        {"id": 2, "type": "emergencia"},
    ]
    result = service.list_plans()

    assert len(result) == 2
    repo.list_all.assert_called_once()


def test_tu_plan_service_02_list_plans_com_repositorio_vazio_devolve_lista_vazia(service, repo):
    """EC-PSVC-LIST-V2 — Repositório vazio → lista vazia devolvida (caso limite)."""
    repo.list_all.return_value = []
    result = service.list_plans()

    assert result == []


# ---------------------------------------------------------------------------
# get_plan
# ---------------------------------------------------------------------------

def test_tu_plan_service_03_get_plan_com_id_existente_devolve_plano(service, repo):
    """EC-PSVC-GET-V1 — id existente no repositório → plano correspondente devolvido."""
    repo.find_by_id.return_value = {"id": 1, "type": "regular"}

    result = service.get_plan(1)

    assert result["id"] == 1
    repo.find_by_id.assert_called_once_with(1)


def test_tu_plan_service_04_get_plan_com_id_inexistente_lanca_plan_not_found(service, repo):
    """EC-PSVC-GET-I1 — id inexistente no repositório → lança PlanNotFound."""
    repo.find_by_id.return_value = None

    with pytest.raises(PlanNotFound):
        service.get_plan(999)


# ---------------------------------------------------------------------------
# create_plan — PE
# ---------------------------------------------------------------------------

def test_tu_plan_service_05_create_plan_valido_guarda_e_devolve(service, repo):
    """EC-PSVC-CREATE-V1 — Dados válidos tipo 'regular' → plano validado, guardado e devolvido."""
    repo.save.return_value = {**VALID_PLAN_DATA, "id": 1, "authorized_by": None}

    result = service.create_plan(VALID_PLAN_DATA)

    repo.save.assert_called_once()
    assert result["id"] == 1


def test_tu_plan_service_06_create_plan_com_tipo_invalido_lanca_plan_validation_error(service, repo):
    """EC-PSVC-CREATE-I1 — Tipo de plano inválido → PlanValidationError propagada do validator."""
    data = {**VALID_PLAN_DATA, "type": "desconhecido"}

    with pytest.raises(PlanValidationError):
        service.create_plan(data)

    repo.save.assert_not_called()


def test_tu_plan_service_07_create_plan_com_temp_fora_do_intervalo_lanca_validation_error(service, repo):
    """EC-PSVC-CREATE-I1 — temp_min abaixo do mínimo → PlanValidationError propagada do validator."""
    data = {**VALID_PLAN_DATA, "temp_min": 5.0}

    with pytest.raises(PlanValidationError):
        service.create_plan(data)

    repo.save.assert_not_called()


# ---------------------------------------------------------------------------
# create_plan — MC/DC (decisão pontual + authorized_by)
# ---------------------------------------------------------------------------

def test_tu_plan_service_08_create_plan_pontual_com_auth_aceite(service, repo):
    """EC-PSVC-CREATE-V2 | MC/DC C1=T, C2=T — Plano pontual com authorized_by → aceite e guardado."""
    data = {**VALID_PLAN_DATA, "type": "pontual"}
    repo.save.return_value = {**data, "id": 1, "authorized_by": 3}

    result = service.create_plan(data, authorized_by=3)

    repo.save.assert_called_once()
    assert result["authorized_by"] == 3


def test_tu_plan_service_09_create_plan_pontual_sem_auth_lanca_unauthorized(service, repo):
    """EC-PSVC-CREATE-I2 | MC/DC C1=T, C2=F — Plano pontual sem authorized_by → UnauthorizedPontualPlan."""
    data = {**VALID_PLAN_DATA, "type": "pontual"}

    with pytest.raises(UnauthorizedPontualPlan):
        service.create_plan(data, authorized_by=None)

    repo.save.assert_not_called()


def test_tu_plan_service_10_create_plan_regular_com_auth_aceite(service, repo):
    """EC-PSVC-CREATE-V1 | MC/DC C1=F, C2=T — Plano regular com authorized_by → aceite (auth ignorada)."""
    repo.save.return_value = {**VALID_PLAN_DATA, "id": 1, "authorized_by": 3}

    result = service.create_plan(VALID_PLAN_DATA, authorized_by=3)

    repo.save.assert_called_once()


def test_tu_plan_service_11_create_plan_regular_sem_auth_aceite(service, repo):
    """EC-PSVC-CREATE-V1 | MC/DC C1=F, C2=F — Plano regular sem authorized_by → aceite."""
    repo.save.return_value = {**VALID_PLAN_DATA, "id": 1, "authorized_by": None}

    result = service.create_plan(VALID_PLAN_DATA, authorized_by=None)

    repo.save.assert_called_once()
