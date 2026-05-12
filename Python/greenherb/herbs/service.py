from greenherb.herbs.importer import parse_csv
from greenherb.herbs.exceptions import HerbNotFound, HerbValidationError


class HerbService:
    def __init__(self, repository):
        self.repository = repository

    def list_herbs(self) -> list:
        return self.repository.list_all()

    def get_herb(self, herb_id: int) -> dict:
        herb = self.repository.find_by_id(herb_id)
        if herb is None:
            raise HerbNotFound(f"Erva com id={herb_id} não encontrada")
        return herb

    def create_herb(self, data: dict) -> dict:
        if not data.get("name", "").strip():
            raise HerbValidationError("O campo 'name' é obrigatório")
        if not data.get("family", "").strip():
            raise HerbValidationError("O campo 'family' é obrigatório")
        return self.repository.save(data)

    def import_from_csv(self, csv_content: str) -> dict:
        """
        Importa ervas a partir de conteúdo CSV.
        Persiste apenas as linhas classificadas como 'valid'.
        Devolve o relatório completo com valid/partial/invalid e totals.
        """
        report = parse_csv(csv_content)

        if report["valid"]:
            self.repository.save_many(report["valid"])

        return report
