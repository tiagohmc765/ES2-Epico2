from greenherb.plans.validator import validate_plan
from greenherb.plans.exceptions import PlanNotFound


class PlanService:
    def __init__(self, repository, herb_repository=None):
        self.repository = repository
        self.herb_repository = herb_repository

    def list_plans(self) -> list:
        return self.repository.list_all()

    def get_plan(self, plan_id: int) -> dict:
        plan = self.repository.find_by_id(plan_id)
        if plan is None:
            raise PlanNotFound(f"Plano com id={plan_id} não encontrado")
        return plan

    def create_plan(self, data: dict, authorized_by: int | None = None) -> dict:
        validated = validate_plan(data, authorized_by=authorized_by)
        return self.repository.save(validated)
