"""
Testes unitários — Máquina de Estados de Lote (transition_state)
=================================================================
Técnicas aplicadas:
    PE  — Particionamento de Equivalência
    MC/DC — Modified Condition/Decision Coverage

Decisão composta para concluir (MC/DC):
    pode_concluir = C1 AND C2
    C1 — new_state == "concluído"
    C2 — end_date is not None

Transições permitidas:
    ativo        → concluído     (requer end_date)
    ativo        → comprometido  (sem requisito extra)
    comprometido → ativo         (reativação)
    concluído    → (nenhuma)     (terminal)

Classes de equivalência (PE):
    V1 — transição ativo → comprometido         → sucesso
    V2 — transição ativo → concluído + end_date → sucesso
    V3 — transição comprometido → ativo         → sucesso
    I1 — transição proibida (concluído → ativo) → BatchValidationError
    I2 — transição ativo → concluído sem end_date → BatchValidationError
    I3 — estado atual inválido                  → BatchValidationError
    I4 — novo estado inválido                   → BatchValidationError
"""

import pytest
from greenherb.batches.state_machine import transition_state
from greenherb.batches.exceptions import BatchValidationError


# ---------------------------------------------------------------------------
# PE — Classe V1: ativo → comprometido
# ---------------------------------------------------------------------------

class TestPE_V1_AtivoParaComprometido:
    """V1 — transição ativo → comprometido: sempre permitida."""

    def test_v1_ativo_para_comprometido(self):
        result = transition_state("ativo", "comprometido")
        assert result["previous_state"] == "ativo"
        assert result["new_state"] == "comprometido"

    def test_v1_ativo_para_comprometido_sem_end_date(self):
        result = transition_state("ativo", "comprometido", end_date=None)
        assert result["new_state"] == "comprometido"


# ---------------------------------------------------------------------------
# PE — Classe V2: ativo → concluído com end_date
# ---------------------------------------------------------------------------

class TestPE_V2_AtivoParaConcluido:
    """V2 — transição ativo → concluído com end_date: permitida."""

    def test_v2_ativo_para_concluido_com_end_date(self):
        result = transition_state("ativo", "concluído", end_date="2024-06-30")
        assert result["previous_state"] == "ativo"
        assert result["new_state"] == "concluído"

    def test_v2_retorna_dict_com_estados(self):
        result = transition_state("ativo", "concluído", end_date="2024-12-31")
        assert "previous_state" in result
        assert "new_state" in result


# ---------------------------------------------------------------------------
# PE — Classe V3: comprometido → ativo
# ---------------------------------------------------------------------------

class TestPE_V3_ComprometidoParaAtivo:
    """V3 — reativação: comprometido → ativo."""

    def test_v3_comprometido_para_ativo(self):
        result = transition_state("comprometido", "ativo")
        assert result["previous_state"] == "comprometido"
        assert result["new_state"] == "ativo"


# ---------------------------------------------------------------------------
# PE — Classe I1: transição proibida
# ---------------------------------------------------------------------------

class TestPE_I1_TransicaoProibida:
    """I1 — transições não permitidas pela máquina de estados."""

    def test_i1_concluido_para_ativo(self):
        with pytest.raises(BatchValidationError):
            transition_state("concluído", "ativo")

    def test_i1_concluido_para_comprometido(self):
        with pytest.raises(BatchValidationError):
            transition_state("concluído", "comprometido")

    def test_i1_comprometido_para_concluido(self):
        with pytest.raises(BatchValidationError):
            transition_state("comprometido", "concluído")

    def test_i1_ativo_para_ativo(self):
        with pytest.raises(BatchValidationError):
            transition_state("ativo", "ativo")


# ---------------------------------------------------------------------------
# PE — Classe I2: ativo → concluído sem end_date
# ---------------------------------------------------------------------------

class TestPE_I2_ConcluidoSemEndDate:
    """I2 — concluir lote sem data de fim: BatchValidationError."""

    def test_i2_ativo_para_concluido_sem_end_date(self):
        with pytest.raises(BatchValidationError):
            transition_state("ativo", "concluído")

    def test_i2_ativo_para_concluido_end_date_none(self):
        with pytest.raises(BatchValidationError):
            transition_state("ativo", "concluído", end_date=None)


# ---------------------------------------------------------------------------
# PE — Classe I3: estado atual inválido
# ---------------------------------------------------------------------------

class TestPE_I3_EstadoAtualInvalido:
    """I3 — current_state não reconhecido: BatchValidationError."""

    def test_i3_estado_atual_invalido(self):
        with pytest.raises(BatchValidationError):
            transition_state("inativo", "ativo")

    def test_i3_estado_atual_string_vazia(self):
        with pytest.raises(BatchValidationError):
            transition_state("", "ativo")


# ---------------------------------------------------------------------------
# PE — Classe I4: novo estado inválido
# ---------------------------------------------------------------------------

class TestPE_I4_NovoEstadoInvalido:
    """I4 — new_state não reconhecido: BatchValidationError."""

    def test_i4_novo_estado_invalido(self):
        with pytest.raises(BatchValidationError):
            transition_state("ativo", "cancelado")

    def test_i4_novo_estado_string_vazia(self):
        with pytest.raises(BatchValidationError):
            transition_state("ativo", "")


# ---------------------------------------------------------------------------
# MC/DC — decisão: pode_concluir = C1 AND C2
#
#   Teste     C1 (new=="concluído")  C2 (end_date≠None)  Resultado
#   mc_01     F                      F                    — (outro fluxo)
#   mc_02     T                      T                    concluído ✓
#   mc_03     T                      F                    BatchValidationError ← C2 muda resultado
#   mc_04     F                      T                    comprometido ✓       ← C1 muda resultado
# ---------------------------------------------------------------------------

class TestMCDC_TransitionState:
    """MC/DC — cada condição altera independentemente o resultado de concluir."""

    def test_mc_01_c1f_c2f_outro_estado(self):
        """C1=F, C2=F: new_state != concluído, sem end_date → comprometido."""
        result = transition_state("ativo", "comprometido", end_date=None)
        assert result["new_state"] == "comprometido"

    def test_mc_02_c1t_c2t_pode_concluir(self):
        """C1=T, C2=T: pode_concluir=True → concluído."""
        result = transition_state("ativo", "concluído", end_date="2024-06-30")
        assert result["new_state"] == "concluído"

    def test_mc_03_c1t_c2f_nao_pode_concluir(self):
        """C1=T, C2=F: pode_concluir=False → BatchValidationError (C2 muda resultado vs mc_02)."""
        with pytest.raises(BatchValidationError):
            transition_state("ativo", "concluído", end_date=None)

    def test_mc_04_c1f_c2t_outro_estado(self):
        """C1=F, C2=T: new_state != concluído → comprometido (C1 muda resultado vs mc_02)."""
        result = transition_state("ativo", "comprometido", end_date="2024-06-30")
        assert result["new_state"] == "comprometido"
