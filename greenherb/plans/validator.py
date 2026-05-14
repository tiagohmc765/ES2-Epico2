from greenherb.plans.exceptions import PlanValidationError, UnauthorizedPontualPlan

VALID_PLAN_TYPES = {"regular", "emergencia", "pontual"}

# Intervalos aceitáveis para parâmetros ambientais
TEMP_MIN = 18.0
TEMP_MAX = 28.0
HUMIDITY_MIN = 40.0
HUMIDITY_MAX = 80.0
LUMINOSITY_MIN = 5000.0
LUMINOSITY_MAX = 25000.0
CYCLE_DAYS_MIN = 1
CYCLE_DAYS_MAX = 365


def validate_plan(data: dict, authorized_by: int | None = None) -> dict:
    """
    Valida os dados de um plano de cultivo e devolve o dict limpo.

    Regras:
    - type deve ser 'regular', 'emergencia' ou 'pontual'
    - temp_min e temp_max em [TEMP_MIN, TEMP_MAX]
    - humidity_min e humidity_max em [HUMIDITY_MIN, HUMIDITY_MAX]
    - luminosity_min e luminosity_max em [LUMINOSITY_MIN, LUMINOSITY_MAX]
    - cycle_days em [CYCLE_DAYS_MIN, CYCLE_DAYS_MAX]
    - se type == 'pontual': authorized_by não pode ser None (MC/DC C1+C2)

    Lança:
    - PlanValidationError   — parâmetros fora de intervalo ou tipo inválido
    - UnauthorizedPontualPlan — plano pontual sem autorização
    """
    plan_type = data.get("type", "")
    if plan_type not in VALID_PLAN_TYPES:
        raise PlanValidationError(
            f"Tipo de plano inválido: '{plan_type}'. "
            f"Valores válidos: {', '.join(sorted(VALID_PLAN_TYPES))}"
        )

    _validate_range(data, "temp_min", TEMP_MIN, TEMP_MAX, "Temperatura mínima")
    _validate_range(data, "temp_max", TEMP_MIN, TEMP_MAX, "Temperatura máxima")
    _validate_range(data, "humidity_min", HUMIDITY_MIN, HUMIDITY_MAX, "Humidade mínima")
    _validate_range(data, "humidity_max", HUMIDITY_MIN, HUMIDITY_MAX, "Humidade máxima")
    _validate_range(data, "luminosity_min", LUMINOSITY_MIN, LUMINOSITY_MAX, "Luminosidade mínima")
    _validate_range(data, "luminosity_max", LUMINOSITY_MIN, LUMINOSITY_MAX, "Luminosidade máxima")
    _validate_cycle_days(data)

    # MC/DC: C1 = (type == "pontual"), C2 = (authorized_by is not None)
    # Decisão: se C1 e NOT C2 → rejeitar
    if plan_type == "pontual" and authorized_by is None:
        raise UnauthorizedPontualPlan(
            "Plano pontual requer autorização explícita do Responsável Técnico"
        )

    return {**data, "authorized_by": authorized_by}


def _validate_range(data: dict, field: str, min_val: float, max_val: float, label: str):
    if field not in data:
        raise PlanValidationError(f"Campo obrigatório em falta: '{field}'")
    try:
        value = float(data[field])
    except (TypeError, ValueError):
        raise PlanValidationError(f"{label}: valor não numérico")
    if value < min_val or value > max_val:
        raise PlanValidationError(
            f"{label} fora do intervalo [{min_val}, {max_val}]: recebido {value}"
        )


def _validate_cycle_days(data: dict):
    if "cycle_days" not in data:
        raise PlanValidationError("Campo obrigatório em falta: 'cycle_days'")
    try:
        value = int(data["cycle_days"])
    except (TypeError, ValueError):
        raise PlanValidationError("Duração do ciclo: valor não inteiro")
    if value < CYCLE_DAYS_MIN or value > CYCLE_DAYS_MAX:
        raise PlanValidationError(
            f"Duração do ciclo fora do intervalo [{CYCLE_DAYS_MIN}, {CYCLE_DAYS_MAX}]: recebido {value}"
        )
