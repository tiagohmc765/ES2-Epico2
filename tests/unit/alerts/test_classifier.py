"""
Testes unitários — Classificador de Alertas (classify_alert)
=============================================================
Técnicas aplicadas:
    PE  — Particionamento de Equivalência
    MC/DC — Modified Condition/Decision Coverage

Decisão composta (MC/DC):
    alerta_gerado = (C1 OR C2) AND C3
    Níveis: parametros_fora >= 2 → "Crítico"; == 1 → "Aviso"; C3=False → "Informativo"

Condições atómicas:
    C1 — temperatura fora dos limites do plano
    C2 — humidade fora dos limites do plano
    C3 — sensor_ok == True

Classes de equivalência (PE):
    V1 — todos os parâmetros dentro dos limites        → None
    V2 — apenas temperatura fora, sensor OK            → "Aviso"
    V3 — apenas humidade fora, sensor OK               → "Aviso"
    V4 — ambos os parâmetros fora, sensor OK           → "Crítico"
    V5 — pelo menos um parâmetro fora, sensor com falha → "Informativo"
    I1 — measurement sem chaves válidas                → None (sem comparação possível)
"""

import pytest
from greenherb.alerts.classifier import classify_alert

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

PLAN = {
    "temp_min": 15.0,
    "temp_max": 30.0,
    "humidity_min": 40.0,
    "humidity_max": 80.0,
}


def _meas(temp: float, humidity: float) -> dict:
    return {"temp": temp, "humidity": humidity}


# ---------------------------------------------------------------------------
# PE — Classe V1: todos os parâmetros dentro dos limites → None
# ---------------------------------------------------------------------------

class TestPE_V1_SemViolacoes:
    """V1 — medição completamente dentro dos limites."""

    def test_temp_e_humidity_dentro_dos_limites(self):
        result = classify_alert(_meas(22.0, 60.0), PLAN)
        assert result is None

    def test_temp_no_limite_inferior(self):
        result = classify_alert(_meas(15.0, 60.0), PLAN)
        assert result is None

    def test_temp_no_limite_superior(self):
        result = classify_alert(_meas(30.0, 60.0), PLAN)
        assert result is None

    def test_humidity_no_limite_inferior(self):
        result = classify_alert(_meas(22.0, 40.0), PLAN)
        assert result is None

    def test_humidity_no_limite_superior(self):
        result = classify_alert(_meas(22.0, 80.0), PLAN)
        assert result is None


# ---------------------------------------------------------------------------
# PE — Classe V2: apenas temperatura fora, sensor OK → "Aviso"
# ---------------------------------------------------------------------------

class TestPE_V2_ApenasTemperaturaFora:
    """V2 — só C1=True, C2=False, C3=True → "Aviso"."""

    def test_temp_abaixo_do_minimo(self):
        result = classify_alert(_meas(10.0, 60.0), PLAN)
        assert result == "Aviso"

    def test_temp_acima_do_maximo(self):
        result = classify_alert(_meas(35.0, 60.0), PLAN)
        assert result == "Aviso"


# ---------------------------------------------------------------------------
# PE — Classe V3: apenas humidade fora, sensor OK → "Aviso"
# ---------------------------------------------------------------------------

class TestPE_V3_ApenasHumidadeFora:
    """V3 — C1=False, C2=True, C3=True → "Aviso"."""

    def test_humidity_abaixo_do_minimo(self):
        result = classify_alert(_meas(22.0, 20.0), PLAN)
        assert result == "Aviso"

    def test_humidity_acima_do_maximo(self):
        result = classify_alert(_meas(22.0, 95.0), PLAN)
        assert result == "Aviso"


# ---------------------------------------------------------------------------
# PE — Classe V4: ambos os parâmetros fora, sensor OK → "Crítico"
# ---------------------------------------------------------------------------

class TestPE_V4_AmbosParametrosFora:
    """V4 — C1=True, C2=True, C3=True → "Crítico"."""

    def test_temp_e_humidity_ambos_fora(self):
        result = classify_alert(_meas(5.0, 10.0), PLAN)
        assert result == "Crítico"

    def test_temp_acima_e_humidity_acima(self):
        result = classify_alert(_meas(40.0, 95.0), PLAN)
        assert result == "Crítico"


# ---------------------------------------------------------------------------
# PE — Classe V5: sensor com falha, pelo menos um parâmetro fora → "Informativo"
# ---------------------------------------------------------------------------

class TestPE_V5_SensorComFalha:
    """V5 — C3=False e violação → "Informativo"."""

    def test_sensor_falha_temp_fora(self):
        result = classify_alert(_meas(5.0, 60.0), PLAN, sensor_ok=False)
        assert result == "Informativo"

    def test_sensor_falha_humidity_fora(self):
        result = classify_alert(_meas(22.0, 10.0), PLAN, sensor_ok=False)
        assert result == "Informativo"

    def test_sensor_falha_ambos_fora(self):
        result = classify_alert(_meas(5.0, 10.0), PLAN, sensor_ok=False)
        assert result == "Informativo"


# ---------------------------------------------------------------------------
# PE — Classe I1: measurement sem chaves → None (sem dados para comparar)
# ---------------------------------------------------------------------------

class TestPE_I1_MeasurementVazio:
    """I1 — measurement sem 'temp' nem 'humidity' → None."""

    def test_measurement_sem_chaves(self):
        result = classify_alert({}, PLAN)
        assert result is None


# ---------------------------------------------------------------------------
# MC/DC — decisão: alerta_gerado = (C1 OR C2) AND C3
# Tabela de cobertura MC/DC (cada condição altera independentemente o resultado):
#
#   Teste          C1    C2    C3    (C1 OR C2) AND C3    Resultado
#   mc_01          F     F     T     False                None
#   mc_02          T     F     T     True                 "Aviso"       ← C1 muda resultado
#   mc_03          F     T     T     True                 "Aviso"       ← C2 muda resultado
#   mc_04          T     F     F     False                "Informativo" ← C3 muda resultado (par com mc_02)
#   mc_05 (bónus)  T     T     T     True                 "Crítico"     (ambos fora)
# ---------------------------------------------------------------------------

class TestMCDC_ClassifyAlert:
    """MC/DC — cada condição muda independentemente o resultado."""

    def test_mc_01_c1f_c2f_c3t_sem_alerta(self):
        """C1=F, C2=F, C3=T → None (sem violações)."""
        result = classify_alert(_meas(22.0, 60.0), PLAN, sensor_ok=True)
        assert result is None

    def test_mc_02_c1t_c2f_c3t_aviso(self):
        """C1=T, C2=F, C3=T → 'Aviso' (C1 muda resultado vs mc_01)."""
        result = classify_alert(_meas(5.0, 60.0), PLAN, sensor_ok=True)
        assert result == "Aviso"

    def test_mc_03_c1f_c2t_c3t_aviso(self):
        """C1=F, C2=T, C3=T → 'Aviso' (C2 muda resultado vs mc_01)."""
        result = classify_alert(_meas(22.0, 10.0), PLAN, sensor_ok=True)
        assert result == "Aviso"

    def test_mc_04_c1t_c2f_c3f_informativo(self):
        """C1=T, C2=F, C3=F → 'Informativo' (C3 muda resultado vs mc_02)."""
        result = classify_alert(_meas(5.0, 60.0), PLAN, sensor_ok=False)
        assert result == "Informativo"

    def test_mc_05_c1t_c2t_c3t_critico(self):
        """C1=T, C2=T, C3=T → 'Crítico' (ambos fora, sensor OK)."""
        result = classify_alert(_meas(5.0, 10.0), PLAN, sensor_ok=True)
        assert result == "Crítico"

    def test_mc_06_c1f_c2t_c3f_informativo(self):
        """C1=F, C2=T, C3=F → 'Informativo' (C3 muda resultado vs mc_03)."""
        result = classify_alert(_meas(22.0, 10.0), PLAN, sensor_ok=False)
        assert result == "Informativo"
