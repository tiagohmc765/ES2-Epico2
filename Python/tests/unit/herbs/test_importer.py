import pytest

from greenherb.herbs.importer import parse_csv, classify_row
from greenherb.herbs.exceptions import EmptyImportFile

# ---------------------------------------------------------------------------
# Helpers — construção de CSV inline
# ---------------------------------------------------------------------------

HEADER = "name,family,scientific_name,description,origin"


def make_csv(*rows: str) -> str:
    return HEADER + "\n" + "\n".join(rows)


# ---------------------------------------------------------------------------
# classify_row — Particionamento de Equivalência
# ---------------------------------------------------------------------------

def test_tu_herb_importer_01_linha_com_todos_campos_obrigatorios_e_valida():
    """PE — Classe válida: name e family presentes."""
    row = {"name": "Basil", "family": "Lamiaceae"}
    assert classify_row(row) == "valid"


def test_tu_herb_importer_02_linha_sem_name_e_invalida():
    """PE — Classe inválida: nenhum campo obrigatório útil (só family)."""
    row = {"name": "", "family": "Lamiaceae"}
    assert classify_row(row) == "partial"


def test_tu_herb_importer_03_linha_sem_nenhum_campo_obrigatorio_e_invalida():
    """PE — Classe inválida: name e family em falta."""
    row = {"name": "", "family": ""}
    assert classify_row(row) == "invalid"


def test_tu_herb_importer_04_linha_com_name_mas_sem_family_e_parcial():
    """PE — Classe parcial: name presente mas family em falta."""
    row = {"name": "Basil", "family": ""}
    assert classify_row(row) == "partial"


def test_tu_herb_importer_05_linha_com_apenas_campos_opcionais_e_invalida():
    """PE — Classe inválida: só campos opcionais preenchidos."""
    row = {"name": "", "family": "", "scientific_name": "Ocimum basilicum"}
    assert classify_row(row) == "invalid"


# ---------------------------------------------------------------------------
# parse_csv — ficheiro vazio lança exceção
# ---------------------------------------------------------------------------

def test_tu_herb_importer_06_conteudo_vazio_lanca_empty_import_file():
    """PE — Classe inválida: ficheiro vazio."""
    with pytest.raises(EmptyImportFile):
        parse_csv("")


def test_tu_herb_importer_07_apenas_cabecalho_sem_linhas_lanca_empty_import_file():
    """PE — Classe inválida: ficheiro apenas com cabeçalho, sem dados."""
    with pytest.raises(EmptyImportFile):
        parse_csv(HEADER)


def test_tu_herb_importer_08_conteudo_so_espacos_lanca_empty_import_file():
    """PE — Classe inválida: conteúdo com apenas espaços em branco."""
    with pytest.raises(EmptyImportFile):
        parse_csv("   \n  ")


# ---------------------------------------------------------------------------
# parse_csv — ficheiro com apenas linhas válidas
# ---------------------------------------------------------------------------

def test_tu_herb_importer_09_ficheiro_com_linhas_todas_validas():
    """PE — Classe válida: todas as linhas têm os campos obrigatórios."""
    csv = make_csv(
        "Basil,Lamiaceae,Ocimum basilicum,Aromatic herb,Mediterranean",
        "Rosemary,Lamiaceae,Salvia rosmarinus,Woody herb,Mediterranean",
    )
    result = parse_csv(csv)

    assert result["totals"]["valid"] == 2
    assert result["totals"]["partial"] == 0
    assert result["totals"]["invalid"] == 0
    assert result["totals"]["total"] == 2
    assert len(result["valid"]) == 2


# ---------------------------------------------------------------------------
# parse_csv — ficheiro com apenas linhas inválidas
# ---------------------------------------------------------------------------

def test_tu_herb_importer_10_ficheiro_com_linhas_todas_invalidas():
    """PE — Classe inválida: todas as linhas sem campos obrigatórios."""
    csv = make_csv(
        ",,Ocimum basilicum,,",
        ",,,Woody herb,",
    )
    result = parse_csv(csv)

    assert result["totals"]["valid"] == 0
    assert result["totals"]["invalid"] == 2
    assert result["totals"]["total"] == 2


# ---------------------------------------------------------------------------
# parse_csv — ficheiro misto (válidas + parciais + inválidas)
# ---------------------------------------------------------------------------

def test_tu_herb_importer_11_ficheiro_misto_conta_corretamente_cada_categoria():
    """PE — Classe mista: mix de linhas válidas, parciais e inválidas."""
    csv = make_csv(
        "Basil,Lamiaceae,,,",           # válida
        "Rosemary,,Salvia rosmarinus,,", # parcial (sem family)
        ",,Mentha spicata,,",            # inválida
    )
    result = parse_csv(csv)

    assert result["totals"]["valid"] == 1
    assert result["totals"]["partial"] == 1
    assert result["totals"]["invalid"] == 1
    assert result["totals"]["total"] == 3


# ---------------------------------------------------------------------------
# parse_csv — campos com espaços extra são normalizados
# ---------------------------------------------------------------------------

def test_tu_herb_importer_12_campos_com_espacos_extra_sao_normalizados():
    """PE — Classe válida: espaços à volta dos valores são removidos."""
    csv = make_csv("  Basil  ,  Lamiaceae  ,,,")
    result = parse_csv(csv)

    assert result["totals"]["valid"] == 1
    herb = result["valid"][0]
    assert herb["name"] == "Basil"
    assert herb["family"] == "Lamiaceae"


# ---------------------------------------------------------------------------
# parse_csv — ficheiro com uma única linha válida
# ---------------------------------------------------------------------------

def test_tu_herb_importer_13_ficheiro_com_uma_linha_valida():
    """PE — Caso limite: ficheiro com exatamente uma linha de dados válida."""
    csv = make_csv("Mint,Lamiaceae,,,")
    result = parse_csv(csv)

    assert result["totals"]["valid"] == 1
    assert result["totals"]["total"] == 1
