"""
Classificador de Alertas — GreenHerb
=====================================
Classifica o nível de um alerta com base numa medição ambiental e nos
limites definidos no plano de cultivo associado ao lote.

Decisão principal (MC/DC aplicado):
    alerta_gerado = (temp_fora OR humidity_fora) AND sensor_ok

Condições atómicas:
    C1 — temperatura fora dos limites do plano
    C2 — humidade fora dos limites do plano
    C3 — sensor operacional (sensor_ok == True)

Níveis de alerta:
    "Crítico"     — C3=True  e dois ou mais parâmetros fora dos limites
    "Aviso"       — C3=True  e exatamente um parâmetro fora dos limites
    "Informativo" — C3=False e pelo menos um parâmetro fora dos limites
                    (sensor com falha: leitura incerta, nível mínimo de alerta)
    None          — todos os parâmetros dentro dos limites (sem alerta)
"""

from typing import Optional


def classify_alert(
    measurement: dict,
    plan: dict,
    sensor_ok: bool = True,
) -> Optional[str]:
    """
    Classifica o nível de alerta para uma medição ambiental.

    Args:
        measurement: dicionário com chaves 'temp' e 'humidity' (valores float).
        plan:        dicionário com chaves 'temp_min', 'temp_max',
                     'humidity_min', 'humidity_max' (valores float).
        sensor_ok:   True se o sensor está operacional, False se está com falha.

    Returns:
        "Crítico", "Aviso", "Informativo" ou None.
    """
    temp = measurement.get("temp")
    humidity = measurement.get("humidity")

    # C1: temperatura fora dos limites
    temp_fora = (
        temp is not None
        and (temp < plan["temp_min"] or temp > plan["temp_max"])
    )

    # C2: humidade fora dos limites
    humidity_fora = (
        humidity is not None
        and (humidity < plan["humidity_min"] or humidity > plan["humidity_max"])
    )

    parametros_fora = int(temp_fora) + int(humidity_fora)

    # Sem violações — sem alerta
    if parametros_fora == 0:
        return None

    # C3 = False — sensor com falha: incerteza nas leituras → Informativo
    if not sensor_ok:
        return "Informativo"

    # C3 = True — sensor OK: classificar por gravidade
    if parametros_fora >= 2:
        return "Crítico"
    return "Aviso"
