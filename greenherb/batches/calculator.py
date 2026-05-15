"""
Calculadora de Produtividade de Lote — GreenHerb
==================================================
Calcula métricas de produtividade de um lote de cultivo com base em:
    - quantidade planeada vs colhida
    - perdas registadas
    - duração planeada vs duração real

Classes de equivalência (PE):
    V1 — lote sem perdas e sem divisões   → produtividade = colhido / planeado
    V2 — lote com perdas, sem divisões    → loss_rate > 0
    V3 — lote sem perdas, com divisões    → harvested_qty < planned_qty
    I1 — planned_qty <= 0                 → BatchValidationError
    I2 — actual_days None ou <= 0         → BatchValidationError (sem data de fim)
    I3 — harvested_qty < 0               → BatchValidationError
    I4 — losses < 0                       → BatchValidationError
"""

from greenherb.batches.exceptions import BatchValidationError


def calculate_productivity(
    planned_qty: float,
    harvested_qty: float,
    losses: float,
    planned_days: int,
    actual_days: int | None,
) -> dict:
    """
    Calcula métricas de produtividade de um lote.

    Args:
        planned_qty:   quantidade de produção planeada (kg ou unidades).
        harvested_qty: quantidade efetivamente colhida.
        losses:        perdas registadas ao longo do ciclo.
        planned_days:  duração planeada do ciclo (dias).
        actual_days:   duração real do ciclo (dias); None se o lote ainda não
                       foi concluído.

    Returns:
        dict com 'yield_rate', 'loss_rate', 'time_efficiency',
        'productivity_score'.

    Raises:
        BatchValidationError: se os dados são inválidos ou o lote não tem
                              data de fim real.
    """
    if planned_qty <= 0:
        raise BatchValidationError(
            "A quantidade planeada deve ser positiva."
        )
    if actual_days is None or actual_days <= 0:
        raise BatchValidationError(
            "Lote sem data de fim real: não é possível calcular produtividade."
        )
    if harvested_qty < 0:
        raise BatchValidationError(
            "A quantidade colhida não pode ser negativa."
        )
    if losses < 0:
        raise BatchValidationError(
            "As perdas não podem ser negativas."
        )

    yield_rate = harvested_qty / planned_qty
    loss_rate = losses / planned_qty
    time_efficiency = planned_days / actual_days
    productivity_score = round(yield_rate * time_efficiency, 4)

    return {
        "yield_rate": round(yield_rate, 4),
        "loss_rate": round(loss_rate, 4),
        "time_efficiency": round(time_efficiency, 4),
        "productivity_score": productivity_score,
    }
