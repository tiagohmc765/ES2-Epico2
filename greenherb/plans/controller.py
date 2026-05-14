import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from greenherb.plans.repository import PlanJsonRepository
from greenherb.plans.service import PlanService
from greenherb.plans.exceptions import PlanNotFound, PlanValidationError, UnauthorizedPontualPlan
from greenherb.auth.jwt_provider import JwtProvider
from greenherb.auth.access_control import require_role
from greenherb.auth.exceptions import AuthError, AccessDenied
from greenherb.auth.error_handler import handle_auth_error

router = APIRouter(prefix="/plans", tags=["plans"])

_repository = PlanJsonRepository("data/plans.json")
_service = PlanService(_repository)

_jwt_secret = os.environ.get("JWT_SECRET", "segredo-super-secreto")
_jwt_provider = JwtProvider(secret=_jwt_secret)
_bearer = HTTPBearer(auto_error=False)


def _get_current_user(credentials: Optional[HTTPAuthorizationCredentials]) -> dict:
    if credentials is None or not credentials.credentials.strip():
        raise AccessDenied("Token ausente ou inválido")

    return _jwt_provider.decode(credentials.credentials.strip())


@router.get("")
def list_plans(credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer)):
    try:
        current_user = _get_current_user(credentials)
        require_role(current_user, ["ADMIN", "RESPONSAVEL", "TECNICO"])
        return _service.list_plans()
    except AuthError as e:
        r = handle_auth_error(e)
        raise HTTPException(status_code=r["status_code"], detail=r["body"])


@router.post("", status_code=201)
def create_plan(payload: dict, credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer)):
    try:
        current_user = _get_current_user(credentials)
        require_role(current_user, ["ADMIN", "RESPONSAVEL"])

        # O campo authorized_by é o id do utilizador que autoriza (para planos pontuais).
        # Extraído do payload; se não enviado usa None.
        authorized_by = payload.pop("authorized_by", None)

        return _service.create_plan(payload, authorized_by=authorized_by)
    except UnauthorizedPontualPlan as e:
        raise HTTPException(status_code=403, detail={"error": "UNAUTHORIZED_PONTUAL", "message": str(e)})
    except PlanValidationError as e:
        raise HTTPException(status_code=400, detail={"error": "VALIDATION_ERROR", "message": str(e)})
    except AuthError as e:
        r = handle_auth_error(e)
        raise HTTPException(status_code=r["status_code"], detail=r["body"])


@router.get("/{plan_id}")
def get_plan(plan_id: int, credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer)):
    try:
        current_user = _get_current_user(credentials)
        require_role(current_user, ["ADMIN", "RESPONSAVEL", "TECNICO"])
        return _service.get_plan(plan_id)
    except PlanNotFound as e:
        raise HTTPException(status_code=404, detail={"error": "NOT_FOUND", "message": str(e)})
    except AuthError as e:
        r = handle_auth_error(e)
        raise HTTPException(status_code=r["status_code"], detail=r["body"])
