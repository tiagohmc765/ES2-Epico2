import csv
import io

from greenherb.herbs.exceptions import EmptyImportFile

# Campos obrigatórios de cada linha do CSV
REQUIRED_FIELDS = {"name", "family"}
# Campos opcionais reconhecidos
OPTIONAL_FIELDS = {"scientific_name", "description", "origin"}
ALL_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS


def classify_row(row: dict) -> str:
    """
    Classifica uma linha do CSV como 'valid', 'invalid' ou 'partial'.

    - valid  : todos os campos obrigatórios presentes e não vazios.
    - partial: pelo menos um campo obrigatório presente mas outro em falta/vazio.
    - invalid: nenhum campo obrigatório útil (linha completamente inutilizável).
    """
    present = {f for f in REQUIRED_FIELDS if row.get(f, "").strip()}
    missing = REQUIRED_FIELDS - present

    if not missing:
        return "valid"
    if present:
        return "partial"
    return "invalid"


def parse_csv(content: str) -> dict:
    """
    Passa para a função uma string que segue a estrutura de um ficheiro CSV.

    Devolve um dicionário com:
      - valid   : lista de dicts das linhas válidas
      - partial : lista de dicts das linhas parcialmente válidas
      - invalid : lista de dicts das linhas inválidas
      - totals  : contagens por categoria

    Lança EmptyImportFile se o conteúdo for vazio ou não contiver linhas de dados.
    """
    content = content.strip()
    if not content:
        raise EmptyImportFile("Ficheiro de importação está vazio")

    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)

    if not rows:
        raise EmptyImportFile("Ficheiro de importação não contém linhas de dados")

    result: dict = {"valid": [], "partial": [], "invalid": []}

    for row in rows:
        # Normalizar chaves (strip de espaços)
        normalized = {k.strip(): v.strip() if v else "" for k, v in row.items()}
        classification = classify_row(normalized)
        result[classification].append(normalized)

    result["totals"] = {
        "valid": len(result["valid"]),
        "partial": len(result["partial"]),
        "invalid": len(result["invalid"]),
        "total": len(rows),
    }

    return result
