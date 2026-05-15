"""
Testes unitários — Calculadora de Produtividade de Lote (calculate_productivity)
==================================================================================
Técnicas aplicadas:
    PE  — Particionamento de Equivalência
    VL  — Análise de Valores Limite (planned_qty > 0, actual_days > 0)

Classes de equivalência (PE):
    V1 — lote sem perdas e sem divisões (colhido = planeado)   → yield_rate=1.0, loss_rate=0.0
    V2 — lote com perdas, sem divisões (losses > 0)            → loss_rate > 0
    V3 — lote sem perdas, com divisões (harvested < planned)   → yield_rate < 1.0
    I1 — planned_qty <= 0                                      → BatchValidationError
    I2 — actual_days None ou <= 0                              → BatchValidationError
    I3 — harvested_qty < 0                                     → BatchValidationError
    I4 — losses < 0                                            → BatchValidationError

Valores limite (VL):
    planned_qty:  0 (inválido), 1 (válido)
    actual_days:  None (inválido), 0 (inválido), 1 (válido)
    harvested_qty: -1 (inválido), 0 (válido)
    losses:        -1 (inválido), 0 (válido)
"""

import pytest
from greenherb.batches.calculator import calculate_productivity
from greenherb.batches.exceptions import BatchValidationError


# ---------------------------------------------------------------------------
# PE — Classe V1: sem perdas e sem divisões
# ---------------------------------------------------------------------------

class TestPE_V1_SemPerdasSemDivisoes:
    """V1 — colhido == planeado, sem perdas."""

    def test_v1_yield_rate_100_percent(self):
        result = calculate_productivity(
            planned_qty=100.0,
            harvested_qty=100.0,
            losses=0.0,
            planned_days=30,
            actual_days=30,
        )
        assert result["yield_rate"] == 1.0
        assert result["loss_rate"] == 0.0
        assert result["time_efficiency"] == 1.0

    def test_v1_productivity_score_calculado(self):
        result = calculate_productivity(
            planned_qty=200.0,
            harvested_qty=200.0,
            losses=0.0,
            planned_days=20,
            actual_days=20,
        )
        assert result["productivity_score"] == 1.0

    def test_v1_eficiencia_temporal_antecipado(self):
        """Lote concluído mais cedo: time_efficiency > 1."""
        result = calculate_productivity(
            planned_qty=100.0,
            harvested_qty=100.0,
            losses=0.0,
            planned_days=30,
            actual_days=20,
        )
        assert result["time_efficiency"] > 1.0


# ---------------------------------------------------------------------------
# PE — Classe V2: com perdas
# ---------------------------------------------------------------------------

class TestPE_V2_ComPerdas:
    """V2 — losses > 0: loss_rate deve ser positivo."""

    def test_v2_loss_rate_positivo(self):
        result = calculate_productivity(
            planned_qty=100.0,
            harvested_qty=80.0,
            losses=20.0,
            planned_days=30,
            actual_days=30,
        )
        assert result["loss_rate"] == pytest.approx(0.2, abs=1e-4)

    def test_v2_yield_rate_com_perdas(self):
        result = calculate_productivity(
            planned_qty=100.0,
            harvested_qty=70.0,
            losses=30.0,
            planned_days=30,
            actual_days=30,
        )
        assert result["yield_rate"] == pytest.approx(0.7, abs=1e-4)
        assert result["loss_rate"] == pytest.approx(0.3, abs=1e-4)


# ---------------------------------------------------------------------------
# PE — Classe V3: sem perdas, com divisões (harvested < planned)
# ---------------------------------------------------------------------------

class TestPE_V3_SemPerdasComDivisoes:
    """V3 — harvested_qty < planned_qty e losses=0: yield_rate < 1."""

    def test_v3_yield_rate_menor_que_1(self):
        result = calculate_productivity(
            planned_qty=100.0,
            harvested_qty=60.0,
            losses=0.0,
            planned_days=30,
            actual_days=30,
        )
        assert result["yield_rate"] == pytest.approx(0.6, abs=1e-4)
        assert result["loss_rate"] == 0.0


# ---------------------------------------------------------------------------
# PE — Classe I1: planned_qty <= 0
# ---------------------------------------------------------------------------

class TestPE_I1_PlannedQtyInvalida:
    """I1 — quantidade planeada não positiva: BatchValidationError."""

    def test_i1_planned_qty_zero(self):
        with pytest.raises(BatchValidationError):
            calculate_productivity(0.0, 100.0, 0.0, 30, 30)

    def test_i1_planned_qty_negativa(self):
        with pytest.raises(BatchValidationError):
            calculate_productivity(-10.0, 100.0, 0.0, 30, 30)


# ---------------------------------------------------------------------------
# PE — Classe I2: actual_days None ou <= 0
# ---------------------------------------------------------------------------

class TestPE_I2_ActualDaysInvalido:
    """I2 — lote sem data de fim real: BatchValidationError."""

    def test_i2_actual_days_none(self):
        with pytest.raises(BatchValidationError):
            calculate_productivity(100.0, 80.0, 0.0, 30, None)

    def test_i2_actual_days_zero(self):
        with pytest.raises(BatchValidationError):
            calculate_productivity(100.0, 80.0, 0.0, 30, 0)

    def test_i2_actual_days_negativo(self):
        with pytest.raises(BatchValidationError):
            calculate_productivity(100.0, 80.0, 0.0, 30, -5)


# ---------------------------------------------------------------------------
# PE — Classe I3: harvested_qty < 0
# ---------------------------------------------------------------------------

class TestPE_I3_HarvestedQtyNegativa:
    """I3 — quantidade colhida negativa: BatchValidationError."""

    def test_i3_harvested_qty_negativa(self):
        with pytest.raises(BatchValidationError):
            calculate_productivity(100.0, -10.0, 0.0, 30, 30)


# ---------------------------------------------------------------------------
# PE — Classe I4: losses < 0
# ---------------------------------------------------------------------------

class TestPE_I4_LossesNegativas:
    """I4 — perdas negativas: BatchValidationError."""

    def test_i4_losses_negativas(self):
        with pytest.raises(BatchValidationError):
            calculate_productivity(100.0, 80.0, -5.0, 30, 30)


# ---------------------------------------------------------------------------
# VL — planned_qty: 0 (inválido), 1 (válido)
# ---------------------------------------------------------------------------

class TestVL_PlannedQty:
    """VL — fronteira de planned_qty."""

    def test_vl_planned_qty_0_invalido(self):
        with pytest.raises(BatchValidationError):
            calculate_productivity(0, 0.0, 0.0, 30, 30)

    def test_vl_planned_qty_1_valido(self):
        result = calculate_productivity(1, 1.0, 0.0, 30, 30)
        assert result["yield_rate"] == 1.0


# ---------------------------------------------------------------------------
# VL — actual_days: None/0 inválidos, 1 válido
# ---------------------------------------------------------------------------

class TestVL_ActualDays:
    """VL — fronteira de actual_days."""

    def test_vl_actual_days_none_invalido(self):
        with pytest.raises(BatchValidationError):
            calculate_productivity(100.0, 80.0, 0.0, 30, None)

    def test_vl_actual_days_0_invalido(self):
        with pytest.raises(BatchValidationError):
            calculate_productivity(100.0, 80.0, 0.0, 30, 0)

    def test_vl_actual_days_1_valido(self):
        result = calculate_productivity(100.0, 80.0, 0.0, 30, 1)
        assert result["time_efficiency"] == 30.0


# ---------------------------------------------------------------------------
# VL — harvested_qty e losses: -1 inválido, 0 válido
# ---------------------------------------------------------------------------

class TestVL_HarvestedELosses:
    """VL — fronteira de harvested_qty e losses."""

    def test_vl_harvested_minus1_invalido(self):
        with pytest.raises(BatchValidationError):
            calculate_productivity(100.0, -1.0, 0.0, 30, 30)

    def test_vl_harvested_0_valido(self):
        result = calculate_productivity(100.0, 0.0, 0.0, 30, 30)
        assert result["yield_rate"] == 0.0

    def test_vl_losses_minus1_invalido(self):
        with pytest.raises(BatchValidationError):
            calculate_productivity(100.0, 80.0, -1.0, 30, 30)

    def test_vl_losses_0_valido(self):
        result = calculate_productivity(100.0, 80.0, 0.0, 30, 30)
        assert result["loss_rate"] == 0.0
