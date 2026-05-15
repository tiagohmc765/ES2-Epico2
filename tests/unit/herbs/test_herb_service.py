import pytest
from unittest.mock import MagicMock, patch

from greenherb.herbs.service import HerbService
from greenherb.herbs.exceptions import HerbNotFound, HerbValidationError, EmptyImportFile

# ===========================================================================
# PARTICIONAMENTO DE EQUIVALÊNCIA — HerbService
#
# Domínio: métodos list_herbs, get_herb, create_herb, import_from_csv
#
# list_herbs:
#   EC-SVC-LIST-V1  Repositório com ervas → lista devolvida
#   EC-SVC-LIST-V2  Repositório vazio → lista vazia (caso limite)
#
# get_herb(herb_id):
#   EC-SVC-GET-V1   id existente no repositório → erva devolvida
#   EC-SVC-GET-I1   id inexistente → lança HerbNotFound
#
# create_herb(data):
#   EC-SVC-CREATE-V1  name e family presentes e não vazios → erva criada
#   EC-SVC-CREATE-I1  name ausente ou só espaços → HerbValidationError
#   EC-SVC-CREATE-I2  family ausente ou só espaços → HerbValidationError
#
# import_from_csv(csv_content):
#   EC-SVC-IMPORT-V1  CSV com linhas válidas → save_many chamado, relatório devolvido
#   EC-SVC-IMPORT-I1  CSV vazio → EmptyImportFile propagada (repo não é acedido)
#   EC-SVC-IMPORT-I2  CSV sem linhas válidas → relatório devolvido, save_many NÃO chamado
#
# ===========================================================================
# MC/DC — import_from_csv
#
# Decisão: if report["valid"]: → self.repository.save_many(report["valid"])
# C1 = report["valid"] é não vazio (lista com pelo menos 1 erva válida)
#
#   MC/DC-C1=T (EC-SVC-IMPORT-V1):  CSV com válidas → save_many chamado
#   MC/DC-C1=F (EC-SVC-IMPORT-I2):  CSV sem válidas → save_many NÃO chamado
# ===========================================================================


@pytest.fixture
def repo():
    return MagicMock()


@pytest.fixture
def service(repo):
    return HerbService(repository=repo)


# ---------------------------------------------------------------------------
# list_herbs
# ---------------------------------------------------------------------------

def test_tu_herb_service_01_list_herbs_com_ervas_devolve_lista(service, repo):
    """EC-SVC-LIST-V1 — Repositório com ervas → lista com todas as ervas devolvida."""
    repo.list_all.return_value = [
        {"id": 1, "name": "Basil", "family": "Lamiaceae"},
        {"id": 2, "name": "Rosemary", "family": "Lamiaceae"},
    ]
    result = service.list_herbs()

    assert len(result) == 2
    assert result[0]["name"] == "Basil"
    repo.list_all.assert_called_once()


def test_tu_herb_service_02_list_herbs_com_repositorio_vazio_devolve_lista_vazia(service, repo):
    """EC-SVC-LIST-V2 — Repositório vazio → lista vazia devolvida (caso limite)."""
    repo.list_all.return_value = []
    result = service.list_herbs()

    assert result == []
    repo.list_all.assert_called_once()


# ---------------------------------------------------------------------------
# get_herb
# ---------------------------------------------------------------------------

def test_tu_herb_service_03_get_herb_com_id_existente_devolve_erva(service, repo):
    """EC-SVC-GET-V1 — id existente no repositório → erva correspondente devolvida."""
    repo.find_by_id.return_value = {"id": 1, "name": "Basil", "family": "Lamiaceae"}

    result = service.get_herb(1)

    assert result["id"] == 1
    assert result["name"] == "Basil"
    repo.find_by_id.assert_called_once_with(1)


def test_tu_herb_service_04_get_herb_com_id_inexistente_lanca_herb_not_found(service, repo):
    """EC-SVC-GET-I1 — id inexistente no repositório → lança HerbNotFound."""
    repo.find_by_id.return_value = None

    with pytest.raises(HerbNotFound):
        service.get_herb(999)


# ---------------------------------------------------------------------------
# create_herb
# ---------------------------------------------------------------------------

def test_tu_herb_service_05_create_herb_com_dados_validos_guarda_e_devolve(service, repo):
    """EC-SVC-CREATE-V1 — name e family presentes → erva criada e guardada no repositório."""
    repo.save.return_value = {"id": 1, "name": "Basil", "family": "Lamiaceae"}
    data = {"name": "Basil", "family": "Lamiaceae"}

    result = service.create_herb(data)

    assert result["id"] == 1
    repo.save.assert_called_once_with(data)


def test_tu_herb_service_06_create_herb_sem_name_lanca_herb_validation_error(service, repo):
    """EC-SVC-CREATE-I1 — name ausente do dicionário → HerbValidationError."""
    with pytest.raises(HerbValidationError):
        service.create_herb({"family": "Lamiaceae"})

    repo.save.assert_not_called()


def test_tu_herb_service_07_create_herb_com_name_vazio_lanca_herb_validation_error(service, repo):
    """EC-SVC-CREATE-I1 — name presente mas só espaços em branco → HerbValidationError."""
    with pytest.raises(HerbValidationError):
        service.create_herb({"name": "   ", "family": "Lamiaceae"})

    repo.save.assert_not_called()


def test_tu_herb_service_08_create_herb_sem_family_lanca_herb_validation_error(service, repo):
    """EC-SVC-CREATE-I2 — family ausente do dicionário → HerbValidationError."""
    with pytest.raises(HerbValidationError):
        service.create_herb({"name": "Basil"})

    repo.save.assert_not_called()


def test_tu_herb_service_09_create_herb_com_family_vazia_lanca_herb_validation_error(service, repo):
    """EC-SVC-CREATE-I2 — family presente mas só espaços em branco → HerbValidationError."""
    with pytest.raises(HerbValidationError):
        service.create_herb({"name": "Basil", "family": "  "})

    repo.save.assert_not_called()


# ---------------------------------------------------------------------------
# import_from_csv — PE + MC/DC
# ---------------------------------------------------------------------------

def test_tu_herb_service_10_import_csv_com_validas_chama_save_many(service, repo):
    """EC-SVC-IMPORT-V1 | MC/DC C1=T — CSV com linhas válidas → save_many chamado com as válidas."""
    csv_content = (
        "name,family,scientific_name,description,origin\n"
        "Basil,Lamiaceae,,,\n"
        "Rosemary,Lamiaceae,,,\n"
    )
    repo.save_many.return_value = [
        {"id": 1, "name": "Basil", "family": "Lamiaceae"},
        {"id": 2, "name": "Rosemary", "family": "Lamiaceae"},
    ]

    result = service.import_from_csv(csv_content)

    repo.save_many.assert_called_once()
    assert result["totals"]["valid"] == 2


def test_tu_herb_service_11_import_csv_sem_validas_nao_chama_save_many(service, repo):
    """EC-SVC-IMPORT-I2 | MC/DC C1=F — CSV sem linhas válidas → save_many NÃO chamado."""
    csv_content = (
        "name,family,scientific_name,description,origin\n"
        ",,Ocimum basilicum,,\n"
    )

    result = service.import_from_csv(csv_content)

    repo.save_many.assert_not_called()
    assert result["totals"]["valid"] == 0
    assert result["totals"]["invalid"] == 1


def test_tu_herb_service_12_import_csv_vazio_lanca_empty_import_file(service, repo):
    """EC-SVC-IMPORT-I1 — CSV vazio → EmptyImportFile propagada; repositório não é acedido."""
    with pytest.raises(EmptyImportFile):
        service.import_from_csv("")

    repo.save_many.assert_not_called()


def test_tu_herb_service_13_import_csv_devolve_relatorio_com_todas_as_categorias(service, repo):
    """EC-SVC-IMPORT-V1 — CSV misto → relatório com valid/partial/invalid e totals corretos."""
    csv_content = (
        "name,family,scientific_name,description,origin\n"
        "Basil,Lamiaceae,,,\n"       # válida
        "Rosemary,,Salvia rosmarinus,,\n"  # parcial
        ",,Mentha spicata,,\n"         # inválida
    )
    repo.save_many.return_value = [{"id": 1, "name": "Basil", "family": "Lamiaceae"}]

    result = service.import_from_csv(csv_content)

    assert result["totals"]["valid"] == 1
    assert result["totals"]["partial"] == 1
    assert result["totals"]["invalid"] == 1
    assert result["totals"]["total"] == 3
