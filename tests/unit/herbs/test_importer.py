import pathlib

import pytest

from greenherb.herbs.importer import parse_csv, classify_row
from greenherb.herbs.exceptions import EmptyImportFile

# ---------------------------------------------------------------------------
# Caminho para os ficheiros CSV de fixture
# ---------------------------------------------------------------------------

FIXTURES = pathlib.Path(__file__).parent.parent.parent / "fixtures" / "herbs"


def read_fixture(filename: str) -> str:
    return (FIXTURES / filename).read_text(encoding="utf-8")


# ===========================================================================
# PARTICIONAMENTO DE EQUIVALÊNCIA — classify_row(row: dict)
#
# Domínio de entrada: dicionário com campos de uma linha CSV
#
# Classes Válidas:
#   EC-ROW-V1  Ambos os campos obrigatórios (name e family) presentes e não vazios
#              → resultado: "valid"
#
# Classes Inválidas:
#   EC-ROW-P1  Exatamente um campo obrigatório presente e não vazio
#              → resultado: "partial"
#   EC-ROW-I1  Nenhum campo obrigatório presente (ambos ausentes ou vazios)
#              → resultado: "invalid"
#   EC-ROW-I2  Só campos opcionais preenchidos, obrigatórios ausentes/vazios
#              → resultado: "invalid"
# ===========================================================================

def test_tu_herb_importer_01_linha_com_todos_campos_obrigatorios_e_valida():
    """EC-ROW-V1 — Classe válida: name e family presentes e não vazios → 'valid'."""
    row = {"name": "Basil", "family": "Lamiaceae"}
    assert classify_row(row) == "valid"


def test_tu_herb_importer_02_linha_sem_name_e_parcial():
    """EC-ROW-P1 — Classe parcial: name vazio, só family presente → 'partial'."""
    row = {"name": "", "family": "Lamiaceae"}
    assert classify_row(row) == "partial"


def test_tu_herb_importer_03_linha_sem_nenhum_campo_obrigatorio_e_invalida():
    """EC-ROW-I1 — Classe inválida: name e family ambos vazios → 'invalid'."""
    row = {"name": "", "family": ""}
    assert classify_row(row) == "invalid"


def test_tu_herb_importer_04_linha_com_name_mas_sem_family_e_parcial():
    """EC-ROW-P1 — Classe parcial: name presente mas family vazio → 'partial'."""
    row = {"name": "Basil", "family": ""}
    assert classify_row(row) == "partial"


def test_tu_herb_importer_05_linha_com_apenas_campos_opcionais_e_invalida():
    """EC-ROW-I2 — Classe inválida: só campos opcionais preenchidos → 'invalid'."""
    row = {"name": "", "family": "", "scientific_name": "Ocimum basilicum"}
    assert classify_row(row) == "invalid"


# ===========================================================================
# PARTICIONAMENTO DE EQUIVALÊNCIA — parse_csv(content: str)
#
# Domínio de entrada: conteúdo de um ficheiro CSV (string)
#
# Classes Válidas:
#   EC-CSV-V1  Ficheiro com cabeçalho + pelo menos 1 linha de dados, delimitador ','
#              → parse bem-sucedido; linhas classificadas em valid/partial/invalid
#
# Classes Inválidas:
#   EC-CSV-I1  Ficheiro completamente vazio (string vazia ou só whitespace)
#              → lança EmptyImportFile
#   EC-CSV-I2  Ficheiro com cabeçalho mas sem linhas de dados
#              → lança EmptyImportFile
#   EC-CSV-I3  Ficheiro com delimitador errado (ex: ';' em vez de ',')
#              → parse não reconhece os campos; todas as linhas inválidas
#   EC-CSV-I4  Ficheiro sem cabeçalho (primeira linha são dados, não nomes de colunas)
#              → campos obrigatórios não reconhecidos; linhas classificadas como inválidas
#
# Análise de Valores Limite — número de colunas:
#   VL-COL-4   4 colunas (fronteira inferior: abaixo do esquema de 5)
#   VL-COL-5   5 colunas (valor nominal: esquema completo)
#   VL-COL-6   6 colunas (fronteira superior: acima do esquema de 5)
# ===========================================================================

def test_tu_herb_importer_06_ficheiro_vazio_lanca_empty_import_file():
    """EC-CSV-I1 — Classe inválida: ficheiro completamente vazio → EmptyImportFile."""
    with pytest.raises(EmptyImportFile):
        parse_csv(read_fixture("vazio.csv"))


def test_tu_herb_importer_07_ficheiro_so_com_cabecalho_lanca_empty_import_file():
    """EC-CSV-I2 — Classe inválida: ficheiro com cabeçalho mas sem dados → EmptyImportFile."""
    with pytest.raises(EmptyImportFile):
        parse_csv(read_fixture("so_cabecalho.csv"))


def test_tu_herb_importer_08_ficheiro_so_com_espacos_lanca_empty_import_file():
    """EC-CSV-I1 — Classe inválida: ficheiro só com espaços em branco → EmptyImportFile."""
    with pytest.raises(EmptyImportFile):
        parse_csv(read_fixture("so_espacos.csv"))


def test_tu_herb_importer_09_ficheiro_completo_todas_linhas_validas():
    """EC-CSV-V1 — Classe válida: ficheiro completo com 2 linhas válidas → totais corretos."""
    result = parse_csv(read_fixture("completo.csv"))

    assert result["totals"]["valid"] == 2
    assert result["totals"]["partial"] == 0
    assert result["totals"]["invalid"] == 0
    assert result["totals"]["total"] == 2


def test_tu_herb_importer_10_ficheiro_com_uma_linha_valida():
    """EC-CSV-V1 — Classe válida (caso limite): ficheiro com exatamente 1 linha de dados."""
    result = parse_csv(read_fixture("uma_linha_valida.csv"))

    assert result["totals"]["valid"] == 1
    assert result["totals"]["total"] == 1


def test_tu_herb_importer_11_ficheiro_misto_conta_corretamente_cada_categoria():
    """EC-CSV-V1 — Classe válida (mista): 1 válida + 1 parcial + 1 inválida → contagens corretas."""
    result = parse_csv(read_fixture("misto.csv"))

    assert result["totals"]["valid"] == 1
    assert result["totals"]["partial"] == 1
    assert result["totals"]["invalid"] == 1
    assert result["totals"]["total"] == 3


def test_tu_herb_importer_12_ficheiro_com_todas_linhas_invalidas():
    """EC-CSV-V1 (conteúdo EC-ROW-I1) — Ficheiro válido mas todas as linhas sem campos obrigatórios."""
    result = parse_csv(read_fixture("todas_invalidas.csv"))

    assert result["totals"]["valid"] == 0
    assert result["totals"]["invalid"] == 2
    assert result["totals"]["total"] == 2


def test_tu_herb_importer_13_ficheiro_com_espacos_extra_normaliza_campos():
    """EC-CSV-V1 — Classe válida: espaços à volta dos valores são normalizados antes da classificação."""
    result = parse_csv(read_fixture("espacos_extra.csv"))

    assert result["totals"]["valid"] == 1
    herb = result["valid"][0]
    assert herb["name"] == "Basil"
    assert herb["family"] == "Lamiaceae"


def test_tu_herb_importer_14_ficheiro_com_delimitador_errado_classifica_como_invalido():
    """EC-CSV-I3 — Classe inválida: delimitador ';' — cada linha lida como 1 campo,
    'name' e 'family' nunca encontrados → todas as linhas inválidas."""
    result = parse_csv(read_fixture("delimitador_errado.csv"))

    assert result["totals"]["valid"] == 0
    assert result["totals"]["invalid"] == 2


def test_tu_herb_importer_15_ficheiro_sem_cabecalho_classifica_como_invalido():
    """EC-CSV-I4 — Classe inválida: sem cabeçalho — 1ª linha de dados tratada como header,
    restantes não têm 'name'/'family' → linha restante inválida."""
    result = parse_csv(read_fixture("sem_cabecalho.csv"))

    assert result["totals"]["valid"] == 0
    assert result["totals"]["total"] == 1


def test_tu_herb_importer_16_ficheiro_com_quatro_colunas_fronteira_inferior():
    """VL-COL-4 — Fronteira inferior (4 colunas): coluna 'origin' ausente,
    campos obrigatórios presentes → linhas válidas; coluna em falta ignorada."""
    result = parse_csv(read_fixture("quatro_colunas.csv"))

    assert result["totals"]["valid"] == 2
    assert result["totals"]["total"] == 2


def test_tu_herb_importer_17_ficheiro_com_seis_colunas_fronteira_superior():
    """VL-COL-6 — Fronteira superior (6 colunas): coluna extra desconhecida,
    campos obrigatórios presentes → linhas válidas; coluna extra ignorada."""
    result = parse_csv(read_fixture("seis_colunas.csv"))

    assert result["totals"]["valid"] == 2
    assert result["totals"]["total"] == 2


def test_tu_herb_importer_18_ficheiro_com_linhas_vazias_no_meio_sao_ignoradas():
    """EC-CSV-V1 — Classe válida: linhas vazias no meio são ignoradas pelo
    csv.DictReader; apenas linhas com dados são contabilizadas."""
    result = parse_csv(read_fixture("linhas_vazias_no_meio.csv"))

    assert result["totals"]["valid"] == 2
    assert result["totals"]["invalid"] == 0
    assert result["totals"]["total"] == 2
