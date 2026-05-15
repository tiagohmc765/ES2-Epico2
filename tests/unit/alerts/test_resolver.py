"""
Testes unitários — Resolutor de Alertas (resolve_alert)
========================================================
Técnicas aplicadas:
    PE  — Particionamento de Equivalência
    VL  — Análise de Valores Limite (justificação: [10, 500] chars)

Classes de equivalência (PE):
    V1 — status "Resolvido", sem justificação      → sucesso
    V2 — status "Resolvido", com justificação      → sucesso (justificação ignorada)
    V3 — status "Ignorado", justificação válida    → sucesso
    I1 — status inválido                           → AlertValidationError
    I2 — status "Ignorado", sem justificação       → AlertValidationError
    I3 — status "Ignorado", justificação < 10 chars → AlertValidationError
    I4 — status "Ignorado", justificação > 500 chars → AlertValidationError

Valores limite da justificação (VL) para "Ignorado":
    Fronteira inferior [10]:  9 (inválido), 10 (válido)
    Fronteira superior [500]: 500 (válido), 501 (inválido)
    Ponto interior:           250 (válido)
"""

import pytest
from greenherb.alerts.resolver import resolve_alert
from greenherb.alerts.exceptions import AlertValidationError

# ---------------------------------------------------------------------------
# PE — Classe V1: "Resolvido" sem justificação
# ---------------------------------------------------------------------------

class TestPE_V1_Resolvido_SemJustificacao:
    """V1 — Resolvido sem justificação: sucesso."""

    def test_resolvido_sem_justificacao(self):
        result = resolve_alert("Resolvido")
        assert result["status"] == "Resolvido"
        assert result["justification"] is None

    def test_resolvido_retorna_status_correto(self):
        result = resolve_alert("Resolvido", justification=None)
        assert result["status"] == "Resolvido"


# ---------------------------------------------------------------------------
# PE — Classe V2: "Resolvido" com justificação opcional
# ---------------------------------------------------------------------------

class TestPE_V2_Resolvido_ComJustificacao:
    """V2 — Resolvido com justificação: aceite sem validação de comprimento."""

    def test_resolvido_com_justificacao_curta(self):
        result = resolve_alert("Resolvido", justification="OK")
        assert result["status"] == "Resolvido"
        assert result["justification"] == "OK"

    def test_resolvido_com_justificacao_longa(self):
        result = resolve_alert("Resolvido", justification="x" * 1000)
        assert result["status"] == "Resolvido"


# ---------------------------------------------------------------------------
# PE — Classe V3: "Ignorado" com justificação válida (interior)
# ---------------------------------------------------------------------------

class TestPE_V3_Ignorado_JustificacaoValida:
    """V3 — Ignorado com justificação dentro dos limites: sucesso."""

    def test_ignorado_justificacao_interior(self):
        result = resolve_alert("Ignorado", justification="x" * 50)
        assert result["status"] == "Ignorado"
        assert len(result["justification"]) == 50


# ---------------------------------------------------------------------------
# PE — Classe I1: status inválido
# ---------------------------------------------------------------------------

class TestPE_I1_StatusInvalido:
    """I1 — estado não reconhecido: AlertValidationError."""

    def test_status_invalido_string(self):
        with pytest.raises(AlertValidationError):
            resolve_alert("Pendente")

    def test_status_invalido_string_vazia(self):
        with pytest.raises(AlertValidationError):
            resolve_alert("")

    def test_status_invalido_case_sensitivity(self):
        with pytest.raises(AlertValidationError):
            resolve_alert("resolvido")


# ---------------------------------------------------------------------------
# PE — Classe I2: "Ignorado" sem justificação
# ---------------------------------------------------------------------------

class TestPE_I2_Ignorado_SemJustificacao:
    """I2 — Ignorado sem justificação: AlertValidationError."""

    def test_ignorado_sem_justificacao(self):
        with pytest.raises(AlertValidationError):
            resolve_alert("Ignorado")

    def test_ignorado_justificacao_none(self):
        with pytest.raises(AlertValidationError):
            resolve_alert("Ignorado", justification=None)

    def test_ignorado_justificacao_string_vazia(self):
        with pytest.raises(AlertValidationError):
            resolve_alert("Ignorado", justification="")


# ---------------------------------------------------------------------------
# VL — Fronteira inferior [10]: 9 inválido, 10 válido
# ---------------------------------------------------------------------------

class TestVL_FronteiraInferior:
    """VL — limite mínimo de 10 caracteres."""

    def test_vl_justificacao_9_chars_invalido(self):
        """9 chars: abaixo do mínimo → erro."""
        with pytest.raises(AlertValidationError):
            resolve_alert("Ignorado", justification="a" * 9)

    def test_vl_justificacao_10_chars_valido(self):
        """10 chars: exatamente no mínimo → sucesso."""
        result = resolve_alert("Ignorado", justification="a" * 10)
        assert result["status"] == "Ignorado"


# ---------------------------------------------------------------------------
# VL — Ponto interior [250]
# ---------------------------------------------------------------------------

class TestVL_PontoInterior:
    """VL — ponto interior 250 chars: válido."""

    def test_vl_justificacao_250_chars_valido(self):
        result = resolve_alert("Ignorado", justification="a" * 250)
        assert result["status"] == "Ignorado"


# ---------------------------------------------------------------------------
# VL — Fronteira superior [500]: 500 válido, 501 inválido
# ---------------------------------------------------------------------------

class TestVL_FronteiraSupremada:
    """VL — limite máximo de 500 caracteres."""

    def test_vl_justificacao_500_chars_valido(self):
        """500 chars: exatamente no máximo → sucesso."""
        result = resolve_alert("Ignorado", justification="a" * 500)
        assert result["status"] == "Ignorado"

    def test_vl_justificacao_501_chars_invalido(self):
        """501 chars: acima do máximo → erro."""
        with pytest.raises(AlertValidationError):
            resolve_alert("Ignorado", justification="a" * 501)
