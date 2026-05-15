"""
Máquina de Estados de Lote — GreenHerb
========================================
Gere as transições de estado de um lote de cultivo.

Estados válidos: "ativo", "concluído", "comprometido"

Transições permitidas:
    ativo        → concluído     (requer end_date)
    ativo        → comprometido  (sempre permitido)
    comprometido → ativo         (reativação)
    concluído    → (nenhum)      (estado terminal)

Decisão composta para concluir (MC/DC aplicado):
    pode_concluir = (estado_atual == "ativo") AND (end_date is not None)

Condições atómicas:
    C1 — new_state == "concluído"
    C2 — end_date is not None
"""

from greenherb.batches.exceptions import BatchValidationError

ESTADOS_VALIDOS = {"ativo", "concluído", "comprometido"}

TRANSICOES_PERMITIDAS: dict[str, list[str]] = {
    "ativo":        ["concluído", "comprometido"],
    "comprometido": ["ativo"],
    "concluído":    [],
}


def transition_state(
    current_state: str,
    new_state: str,
    end_date: str | None = None,
) -> dict:
    """
    Executa uma transição de estado de lote.

    Args:
        current_state: estado atual do lote.
        new_state:     estado para o qual se pretende transitar.
        end_date:      data de fim real (obrigatória para concluir).

    Returns:
        dict com 'previous_state' e 'new_state'.

    Raises:
        BatchValidationError: se a transição é proibida ou faltam dados.
    """
    if current_state not in ESTADOS_VALIDOS:
        raise BatchValidationError(
            f"Estado atual inválido: '{current_state}'."
        )
    if new_state not in ESTADOS_VALIDOS:
        raise BatchValidationError(
            f"Novo estado inválido: '{new_state}'."
        )
    if new_state not in TRANSICOES_PERMITIDAS[current_state]:
        raise BatchValidationError(
            f"Transição proibida: '{current_state}' → '{new_state}'."
        )

    # C1=True AND C2=False → não pode concluir sem data de fim
    if new_state == "concluído" and end_date is None:
        raise BatchValidationError(
            "Conclusão de lote requer data de fim real."
        )

    return {"previous_state": current_state, "new_state": new_state}
