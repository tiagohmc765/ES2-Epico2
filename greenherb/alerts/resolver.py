"""
Resolutor de Alertas — GreenHerb
===================================
Resolve ou ignora um alerta, aplicando as regras de negócio:
    - "Resolvido": justificação opcional.
    - "Ignorado":  justificação obrigatória, comprimento entre 10 e 500 caracteres.

Valores limite da justificação: [10, 500] caracteres.
"""

from greenherb.alerts.exceptions import AlertValidationError

ESTADOS_VALIDOS = {"Resolvido", "Ignorado"}
JUSTIFICACAO_MIN = 10
JUSTIFICACAO_MAX = 500


def resolve_alert(status: str, justification: str | None = None) -> dict:
    """
    Resolve ou ignora um alerta.

    Args:
        status:        "Resolvido" ou "Ignorado".
        justification: texto de justificação (obrigatório para "Ignorado").

    Returns:
        dict com 'status' e 'justification'.

    Raises:
        AlertValidationError: se o estado é inválido ou a justificação
                              não cumpre as regras de negócio.
    """
    if status not in ESTADOS_VALIDOS:
        raise AlertValidationError(
            f"Estado inválido: '{status}'. Valores aceites: {ESTADOS_VALIDOS}."
        )

    if status == "Ignorado":
        if not justification:
            raise AlertValidationError(
                "Justificação obrigatória para ignorar um alerta."
            )
        if len(justification) < JUSTIFICACAO_MIN:
            raise AlertValidationError(
                f"Justificação demasiado curta "
                f"({len(justification)} chars; mínimo {JUSTIFICACAO_MIN})."
            )
        if len(justification) > JUSTIFICACAO_MAX:
            raise AlertValidationError(
                f"Justificação demasiado longa "
                f"({len(justification)} chars; máximo {JUSTIFICACAO_MAX})."
            )

    return {"status": status, "justification": justification}
