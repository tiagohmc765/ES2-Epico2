"""
Motor de Regras de Automação — GreenHerb
==========================================
Decide se uma ação deve ser sugerida ou executada automaticamente com
base no modo de operação, na ativação da regra e na medição recente.

Decisão composta (MC/DC aplicado):
    acionar = C1 AND C2 AND C3

Condições atómicas:
    C1 — modo == "Automático"
    C2 — rule_active == True
    C3 — measurement_triggers_rule == True

Resultados:
    "executar"  — C1=True,  C2=True,  C3=True  (modo automático, regra ativa, medição dispara)
    "sugerir"   — C1=False, C2=True,  C3=True  (modo manual, operador decide)
    None        — C2=False OR C3=False          (regra inativa ou medição não dispara)
"""

from typing import Optional
from greenherb.automation.exceptions import AutomationError

MODOS_VALIDOS = {"Manual", "Automático"}


def decide_action(
    mode: str,
    rule_active: bool,
    measurement_triggers_rule: bool,
) -> Optional[str]:
    """
    Decide a ação do motor de automação para uma medição recebida.

    Args:
        mode:                      "Manual" ou "Automático".
        rule_active:               True se a regra está ativa.
        measurement_triggers_rule: True se a medição satisfaz a condição
                                   de disparo da regra.

    Returns:
        "executar", "sugerir" ou None.

    Raises:
        AutomationError: se o modo é inválido.
    """
    if mode not in MODOS_VALIDOS:
        raise AutomationError(
            f"Modo inválido: '{mode}'. Valores aceites: {MODOS_VALIDOS}."
        )

    # C2=False ou C3=False → nenhuma ação
    if not rule_active or not measurement_triggers_rule:
        return None

    # C2=True e C3=True: modo determina o tipo de ação
    if mode == "Automático":   # C1=True
        return "executar"
    return "sugerir"            # C1=False (Manual)
