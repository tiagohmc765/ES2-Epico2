import json
from pathlib import Path

from greenherb.herbs.exceptions import HerbNotFound


class HerbJsonRepository:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def find_by_id(self, herb_id: int):
        herbs = self._load()
        return next((h for h in herbs if h["id"] == herb_id), None)

    def find_by_name(self, name: str):
        herbs = self._load()
        return next((h for h in herbs if h["name"].lower() == name.lower()), None)

    def list_all(self) -> list:
        return self._load()

    def save(self, herb: dict) -> dict:
        herbs = self._load()
        new_id = max((h["id"] for h in herbs), default=0) + 1
        herb = {**herb, "id": new_id}
        herbs.append(herb)
        self._persist(herbs)
        return herb

    def save_many(self, herb_list: list) -> list:
        herbs = self._load()
        next_id = max((h["id"] for h in herbs), default=0) + 1
        saved = []
        for herb in herb_list:
            herb = {**herb, "id": next_id}
            herbs.append(herb)
            saved.append(herb)
            next_id += 1
        self._persist(herbs)
        return saved

    def _load(self) -> list:
        if not self.file_path.exists():
            return []
        content = self.file_path.read_text(encoding="utf-8")
        if not content.strip():
            return []
        return json.loads(content)

    def _persist(self, herbs: list):
        self.file_path.write_text(
            json.dumps(herbs, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
