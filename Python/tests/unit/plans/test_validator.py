import pytest

from greenherb.plans.validator import validate_plan
from greenherb.plans.exceptions import PlanValidationError, UnauthorizedPontualPlan

# ---------------------------------------------------------------------------
# Fixture — plano base válido (regular)
# ---------------------------------------------------------------------------

BASE_PLAN = {
    "type": "regular",
    "herb_id": 1,
    "temp_min": 18.0,
    "temp_max": 28.0,
    "humidity_min": 40.0,
    "humidity_max": 80.0,
    "luminosity_min": 5000.0,
    "luminosity_max": 25000.0,
    "cycle_days": 90,
}


def plan(**overrides):
    return {**BASE_PLAN, **overrides}


# ===========================================================================
# PARTICIONAMENTO DE EQUIVALÊNCIA — Tipo de plano
# ===========================================================================

def test_tu_plan_pe_01_tipo_regular_e_aceite():
    """PE — Classe válida: tipo 'regular'."""
    result = validate_plan(plan(type="regular"))
    assert result["type"] == "regular"


def test_tu_plan_pe_02_tipo_emergencia_e_aceite():
    """PE — Classe válida: tipo 'emergencia'."""
    result = validate_plan(plan(type="emergencia"))
    assert result["type"] == "emergencia"


def test_tu_plan_pe_03_tipo_pontual_com_autorizacao_e_aceite():
    """PE — Classe válida: tipo 'pontual' com authorized_by definido."""
    result = validate_plan(plan(type="pontual"), authorized_by=3)
    assert result["type"] == "pontual"
    assert result["authorized_by"] == 3


def test_tu_plan_pe_04_tipo_invalido_lanca_validation_error():
    """PE — Classe inválida: tipo não reconhecido."""
    with pytest.raises(PlanValidationError, match="Tipo de plano inválido"):
        validate_plan(plan(type="desconhecido"))


def test_tu_plan_pe_05_tipo_vazio_lanca_validation_error():
    """PE — Classe inválida: tipo em branco."""
    with pytest.raises(PlanValidationError):
        validate_plan(plan(type=""))


# ===========================================================================
# ANÁLISE DE VALORES LIMITE — Temperatura [18, 28] °C
# Valores: 17, 18, 23, 28, 29
# ===========================================================================

def test_tu_plan_vl_temp_01_abaixo_do_minimo_17_rejeitado():
    """VL — temp_min < 18: deve rejeitar."""
    with pytest.raises(PlanValidationError, match="Temperatura"):
        validate_plan(plan(temp_min=17.0))


def test_tu_plan_vl_temp_02_limite_inferior_18_aceite():
    """VL — temp_min = 18: deve aceitar (limite inferior)."""
    result = validate_plan(plan(temp_min=18.0))
    assert result["temp_min"] == 18.0


def test_tu_plan_vl_temp_03_valor_nominal_23_aceite():
    """VL — temp_min = 23: valor nominal interior."""
    result = validate_plan(plan(temp_min=23.0))
    assert result["temp_min"] == 23.0


def test_tu_plan_vl_temp_04_limite_superior_28_aceite():
    """VL — temp_max = 28: deve aceitar (limite superior)."""
    result = validate_plan(plan(temp_max=28.0))
    assert result["temp_max"] == 28.0


def test_tu_plan_vl_temp_05_acima_do_maximo_29_rejeitado():
    """VL — temp_max > 28: deve rejeitar."""
    with pytest.raises(PlanValidationError, match="Temperatura"):
        validate_plan(plan(temp_max=29.0))


# ===========================================================================
# ANÁLISE DE VALORES LIMITE — Humidade [40, 80] %
# Valores: 39, 40, 60, 80, 81
# ===========================================================================

def test_tu_plan_vl_hum_01_abaixo_do_minimo_39_rejeitado():
    """VL — humidity_min < 40: deve rejeitar."""
    with pytest.raises(PlanValidationError, match="Humidade"):
        validate_plan(plan(humidity_min=39.0))


def test_tu_plan_vl_hum_02_limite_inferior_40_aceite():
    """VL — humidity_min = 40: deve aceitar."""
    result = validate_plan(plan(humidity_min=40.0))
    assert result["humidity_min"] == 40.0


def test_tu_plan_vl_hum_03_valor_nominal_60_aceite():
    """VL — humidity_min = 60: valor nominal."""
    result = validate_plan(plan(humidity_min=60.0))
    assert result["humidity_min"] == 60.0


def test_tu_plan_vl_hum_04_limite_superior_80_aceite():
    """VL — humidity_max = 80: deve aceitar."""
    result = validate_plan(plan(humidity_max=80.0))
    assert result["humidity_max"] == 80.0


def test_tu_plan_vl_hum_05_acima_do_maximo_81_rejeitado():
    """VL — humidity_max > 80: deve rejeitar."""
    with pytest.raises(PlanValidationError, match="Humidade"):
        validate_plan(plan(humidity_max=81.0))


# ===========================================================================
# ANÁLISE DE VALORES LIMITE — Luminosidade [5000, 25000] lux
# Valores: 4999, 5000, 15000, 25000, 25001
# ===========================================================================

def test_tu_plan_vl_lux_01_abaixo_do_minimo_4999_rejeitado():
    """VL — luminosity_min < 5000: deve rejeitar."""
    with pytest.raises(PlanValidationError, match="Luminosidade"):
        validate_plan(plan(luminosity_min=4999.0))


def test_tu_plan_vl_lux_02_limite_inferior_5000_aceite():
    """VL — luminosity_min = 5000: deve aceitar."""
    result = validate_plan(plan(luminosity_min=5000.0))
    assert result["luminosity_min"] == 5000.0


def test_tu_plan_vl_lux_03_valor_nominal_15000_aceite():
    """VL — luminosity_min = 15000: valor nominal."""
    result = validate_plan(plan(luminosity_min=15000.0))
    assert result["luminosity_min"] == 15000.0


def test_tu_plan_vl_lux_04_limite_superior_25000_aceite():
    """VL — luminosity_max = 25000: deve aceitar."""
    result = validate_plan(plan(luminosity_max=25000.0))
    assert result["luminosity_max"] == 25000.0


def test_tu_plan_vl_lux_05_acima_do_maximo_25001_rejeitado():
    """VL — luminosity_max > 25000: deve rejeitar."""
    with pytest.raises(PlanValidationError, match="Luminosidade"):
        validate_plan(plan(luminosity_max=25001.0))


# ===========================================================================
# ANÁLISE DE VALORES LIMITE — Duração do ciclo [1, 365] dias
# Valores: 0, 1, 90, 365, 366
# ===========================================================================

def test_tu_plan_vl_cycle_01_zero_dias_rejeitado():
    """VL — cycle_days = 0: abaixo do mínimo; deve rejeitar."""
    with pytest.raises(PlanValidationError, match="ciclo"):
        validate_plan(plan(cycle_days=0))


def test_tu_plan_vl_cycle_02_um_dia_aceite():
    """VL — cycle_days = 1: limite inferior; deve aceitar."""
    result = validate_plan(plan(cycle_days=1))
    assert result["cycle_days"] == 1


def test_tu_plan_vl_cycle_03_noventa_dias_aceite():
    """VL — cycle_days = 90: valor nominal; deve aceitar."""
    result = validate_plan(plan(cycle_days=90))
    assert result["cycle_days"] == 90


def test_tu_plan_vl_cycle_04_trezentos_sessenta_cinco_dias_aceite():
    """VL — cycle_days = 365: limite superior; deve aceitar."""
    result = validate_plan(plan(cycle_days=365))
    assert result["cycle_days"] == 365


def test_tu_plan_vl_cycle_05_trezentos_sessenta_seis_dias_rejeitado():
    """VL — cycle_days = 366: acima do máximo; deve rejeitar."""
    with pytest.raises(PlanValidationError, match="ciclo"):
        validate_plan(plan(cycle_days=366))


# ===========================================================================
# MC/DC — Validação do plano pontual
#
# Decisão: permitir criação de plano pontual
# Condições atómicas:
#   C1: type == "pontual"
#   C2: authorized_by is not None
#
# Tabela MC/DC (mínima — cada condição altera isoladamente o resultado):
#
# | Caso       | C1    | C2    | Resultado                   |
# |------------|-------|-------|-----------------------------|
# | MCDC-01    | False | False | aceite (plan regular/emerg) |
# | MCDC-02    | True  | False | rejeitado (pontual sem auth) |
# | MCDC-03    | True  | True  | aceite (pontual com auth)   |
# | MCDC-04    | False | True  | aceite (regular com auth)   |
#
# MCDC-01 vs MCDC-02: C1 varia (F→T), C2=False → resultado muda (aceite→rejeit) ✓
# MCDC-02 vs MCDC-03: C2 varia (F→T), C1=True → resultado muda (rejeit→aceite) ✓
# ===========================================================================

def test_tu_plan_mcdc_01_c1_false_c2_false_plano_regular_aceite():
    """MC/DC — C1=False, C2=False: plan regular sem authorized_by → aceite."""
    result = validate_plan(plan(type="regular"), authorized_by=None)
    assert result["type"] == "regular"
    assert result["authorized_by"] is None


def test_tu_plan_mcdc_02_c1_true_c2_false_pontual_sem_auth_rejeitado():
    """MC/DC — C1=True, C2=False: plan pontual sem authorized_by → rejeitado."""
    with pytest.raises(UnauthorizedPontualPlan):
        validate_plan(plan(type="pontual"), authorized_by=None)


def test_tu_plan_mcdc_03_c1_true_c2_true_pontual_com_auth_aceite():
    """MC/DC — C1=True, C2=True: plan pontual com authorized_by → aceite."""
    result = validate_plan(plan(type="pontual"), authorized_by=3)
    assert result["type"] == "pontual"
    assert result["authorized_by"] == 3


def test_tu_plan_mcdc_04_c1_false_c2_true_plan_regular_com_auth_aceite():
    """MC/DC — C1=False, C2=True: plan regular com authorized_by (ignorado) → aceite."""
    result = validate_plan(plan(type="regular"), authorized_by=3)
    assert result["type"] == "regular"
    assert result["authorized_by"] == 3


# ===========================================================================
# Campos em falta — Particionamento de Equivalência
# ===========================================================================

def test_tu_plan_pe_06_campo_obrigatorio_em_falta_lanca_validation_error():
    """PE — Classe inválida: campo cycle_days em falta."""
    data = {k: v for k, v in BASE_PLAN.items() if k != "cycle_days"}
    with pytest.raises(PlanValidationError, match="cycle_days"):
        validate_plan(data)


def test_tu_plan_pe_07_valor_nao_numerico_em_temperatura_lanca_validation_error():
    """PE — Classe inválida: valor não numérico no campo temp_min."""
    with pytest.raises(PlanValidationError, match="não numérico"):
        validate_plan(plan(temp_min="quente"))


def test_tu_plan_pe_08_campo_temp_min_em_falta_lanca_validation_error():
    """PE — Classe inválida: campo temp_min em falta."""
    data = {k: v for k, v in BASE_PLAN.items() if k != "temp_min"}
    with pytest.raises(PlanValidationError, match="temp_min"):
        validate_plan(data)


def test_tu_plan_pe_09_campo_humidity_min_em_falta_lanca_validation_error():
    """PE — Classe inválida: campo humidity_min em falta."""
    data = {k: v for k, v in BASE_PLAN.items() if k != "humidity_min"}
    with pytest.raises(PlanValidationError, match="humidity_min"):
        validate_plan(data)


def test_tu_plan_pe_10_campo_luminosity_min_em_falta_lanca_validation_error():
    """PE — Classe inválida: campo luminosity_min em falta."""
    data = {k: v for k, v in BASE_PLAN.items() if k != "luminosity_min"}
    with pytest.raises(PlanValidationError, match="luminosity_min"):
        validate_plan(data)


def test_tu_plan_pe_11_valor_nao_inteiro_em_cycle_days_lanca_validation_error():
    """PE — Classe inválida: valor não inteiro no campo cycle_days."""
    with pytest.raises(PlanValidationError, match="não inteiro"):
        validate_plan(plan(cycle_days="muitos"))
