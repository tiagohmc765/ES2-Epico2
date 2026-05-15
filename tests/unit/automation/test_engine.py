"""
Testes unitários — Motor de Automação (decide_action)
=====================================================
Técnicas aplicadas:
    PE    — Particionamento de Equivalência
    MC/DC — Modified Condition/Decision Coverage

Decisão composta (MC/DC):
    acionar = C1 AND C2 AND C3

Condições atómicas:
    C1 — mode == "Automático"
    C2 — rule_active == True
    C3 — measurement_triggers_rule == True

Resultados:
    "executar"  — C1=T, C2=T, C3=T
    "sugerir"   — C1=F, C2=T, C3=T
    None        — C2=F OR C3=F
    AutomationError — mode inválido

Classes de equivalência (PE):
    V1 — Automático, regra ativa, medição dispara   → "executar"
    V2 — Manual, regra ativa, medição dispara       → "sugerir"
    V3 — regra inativa (qualquer modo)              → None
    V4 — medição não dispara (qualquer modo)        → None
    I1 — modo inválido                              → AutomationError

MC/DC — tabela de cobertura:
    Teste    C1    C2    C3    acionar    Resultado
    mc_01    T     T     T     True       "executar"
    mc_02    F     T     T     False      "sugerir"   ← C1 muda resultado vs mc_01
    mc_03    T     F     T     False      None        ← C2 muda resultado vs mc_01
    mc_04    T     T     F     False      None        ← C3 muda resultado vs mc_01
    mc_05    F     F     T     False      None        (C2 dominante)
    mc_06    F     T     F     False      None        (C3 dominante)
    mc_07    T     F     F     False      None        (C2 e C3 False)
    mc_08    F     F     F     False      None        (todos False)
"""

import pytest
from greenherb.automation.engine import decide_action
from greenherb.automation.exceptions import AutomationError


# ---------------------------------------------------------------------------
# PE — Classe V1: Automático + regra ativa + medição dispara → "executar"
# ---------------------------------------------------------------------------

class TestPE_V1_ModoAutomatico_Executar:
    """V1 — todas as condições True em modo Automático."""

    def test_v1_automatico_executa_acao(self):
        result = decide_action("Automático", rule_active=True, measurement_triggers_rule=True)
        assert result == "executar"

    def test_v1_retorna_string_executar(self):
        assert decide_action("Automático", True, True) == "executar"


# ---------------------------------------------------------------------------
# PE — Classe V2: Manual + regra ativa + medição dispara → "sugerir"
# ---------------------------------------------------------------------------

class TestPE_V2_ModoManual_Sugerir:
    """V2 — condições de disparo True mas modo Manual."""

    def test_v2_manual_sugere_acao(self):
        result = decide_action("Manual", rule_active=True, measurement_triggers_rule=True)
        assert result == "sugerir"

    def test_v2_retorna_string_sugerir(self):
        assert decide_action("Manual", True, True) == "sugerir"


# ---------------------------------------------------------------------------
# PE — Classe V3: regra inativa → None
# ---------------------------------------------------------------------------

class TestPE_V3_RegraInativa:
    """V3 — C2=False: nenhuma ação independentemente do modo."""

    def test_v3_automatico_regra_inativa(self):
        result = decide_action("Automático", rule_active=False, measurement_triggers_rule=True)
        assert result is None

    def test_v3_manual_regra_inativa(self):
        result = decide_action("Manual", rule_active=False, measurement_triggers_rule=True)
        assert result is None


# ---------------------------------------------------------------------------
# PE — Classe V4: medição não dispara → None
# ---------------------------------------------------------------------------

class TestPE_V4_MedicaoNaoDispara:
    """V4 — C3=False: nenhuma ação independentemente do modo."""

    def test_v4_automatico_medicao_nao_dispara(self):
        result = decide_action("Automático", rule_active=True, measurement_triggers_rule=False)
        assert result is None

    def test_v4_manual_medicao_nao_dispara(self):
        result = decide_action("Manual", rule_active=True, measurement_triggers_rule=False)
        assert result is None

    def test_v4_regra_inativa_e_medicao_nao_dispara(self):
        result = decide_action("Manual", rule_active=False, measurement_triggers_rule=False)
        assert result is None


# ---------------------------------------------------------------------------
# PE — Classe I1: modo inválido → AutomationError
# ---------------------------------------------------------------------------

class TestPE_I1_ModoInvalido:
    """I1 — mode não reconhecido: AutomationError."""

    def test_i1_modo_invalido_string(self):
        with pytest.raises(AutomationError):
            decide_action("Semiautomático", True, True)

    def test_i1_modo_vazio(self):
        with pytest.raises(AutomationError):
            decide_action("", True, True)

    def test_i1_modo_case_errado(self):
        with pytest.raises(AutomationError):
            decide_action("automático", True, True)

    def test_i1_modo_none_raises(self):
        with pytest.raises((AutomationError, AttributeError, TypeError)):
            decide_action(None, True, True)  # type: ignore


# ---------------------------------------------------------------------------
# MC/DC — decisão: acionar = C1 AND C2 AND C3
# Cada condição deve poder alterar independentemente o resultado final.
# ---------------------------------------------------------------------------

class TestMCDC_DecideAction:
    """MC/DC — cobertura completa da decisão tripla."""

    def test_mc_01_c1t_c2t_c3t_executar(self):
        """C1=T, C2=T, C3=T → 'executar' (caso base)."""
        assert decide_action("Automático", True, True) == "executar"

    def test_mc_02_c1f_c2t_c3t_sugerir(self):
        """C1=F, C2=T, C3=T → 'sugerir' (C1 muda resultado vs mc_01)."""
        assert decide_action("Manual", True, True) == "sugerir"

    def test_mc_03_c1t_c2f_c3t_none(self):
        """C1=T, C2=F, C3=T → None (C2 muda resultado vs mc_01)."""
        assert decide_action("Automático", False, True) is None

    def test_mc_04_c1t_c2t_c3f_none(self):
        """C1=T, C2=T, C3=F → None (C3 muda resultado vs mc_01)."""
        assert decide_action("Automático", True, False) is None

    def test_mc_05_c1f_c2f_c3t_none(self):
        """C1=F, C2=F, C3=T → None."""
        assert decide_action("Manual", False, True) is None

    def test_mc_06_c1f_c2t_c3f_none(self):
        """C1=F, C2=T, C3=F → None."""
        assert decide_action("Manual", True, False) is None

    def test_mc_07_c1t_c2f_c3f_none(self):
        """C1=T, C2=F, C3=F → None."""
        assert decide_action("Automático", False, False) is None

    def test_mc_08_c1f_c2f_c3f_none(self):
        """C1=F, C2=F, C3=F → None (todas False)."""
        assert decide_action("Manual", False, False) is None
