import json
from pathlib import Path


class PlanJsonRepository:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def find_by_id(self, plan_id: int):
        plans = self._load()
        return next((p for p in plans if p["id"] == plan_id), None)

    def list_all(self) -> list:
        return self._load()

    def save(self, plan: dict) -> dict:
        plans = self._load()
        new_id = max((p["id"] for p in plans), default=0) + 1
        plan = {**plan, "id": new_id}
        plans.append(plan)
        self._persist(plans)
        return plan

    def _load(self) -> list:
        if not self.file_path.exists():
            return []
        content = self.file_path.read_text(encoding="utf-8")
        if not content.strip():
            return []
        return json.loads(content)

    def _persist(self, plans: list):
        self.file_path.write_text(
            json.dumps(plans, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
