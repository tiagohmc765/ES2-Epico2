import os

from fastapi import APIRouter, HTTPException, Header

from greenherb.herbs.repository import HerbJsonRepository
from greenherb.herbs.service import HerbService
from greenherb.herbs.exceptions import HerbNotFound, HerbValidationError, EmptyImportFile
from greenherb.auth.jwt_provider import JwtProvider
from greenherb.auth.access_control import require_role
from greenherb.auth.exceptions import AuthError, AccessDenied
from greenherb.auth.error_handler import handle_auth_error

router = APIRouter(prefix="/herbs", tags=["herbs"])

_repository = HerbJsonRepository("data/herbs.json")
_service = HerbService(_repository)

_jwt_secret = os.environ.get("JWT_SECRET", "segredo-super-secreto")
_jwt_provider = JwtProvider(secret=_jwt_secret)


def _get_current_user(authorization: str) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise AccessDenied("Token ausente ou inválido")
    return _jwt_provider.decode(authorization[len("Bearer "):])


@router.get("")
def list_herbs(authorization: str = Header(default="")):
    try:
        current_user = _get_current_user(authorization)
        require_role(current_user, ["ADMIN", "RESPONSAVEL", "TECNICO"])
        return _service.list_herbs()
    except AuthError as e:
        r = handle_auth_error(e)
        raise HTTPException(status_code=r["status_code"], detail=r["body"])


@router.post("", status_code=201)
def create_herb(payload: dict, authorization: str = Header(default="")):
    try:
        current_user = _get_current_user(authorization)
        require_role(current_user, ["ADMIN", "RESPONSAVEL"])
        return _service.create_herb(payload)
    except HerbValidationError as e:
        raise HTTPException(status_code=400, detail={"error": "VALIDATION_ERROR", "message": str(e)})
    except AuthError as e:
        r = handle_auth_error(e)
        raise HTTPException(status_code=r["status_code"], detail=r["body"])


@router.get("/{herb_id}")
def get_herb(herb_id: int, authorization: str = Header(default="")):
    try:
        current_user = _get_current_user(authorization)
        require_role(current_user, ["ADMIN", "RESPONSAVEL", "TECNICO"])
        return _service.get_herb(herb_id)
    except HerbNotFound as e:
        raise HTTPException(status_code=404, detail={"error": "NOT_FOUND", "message": str(e)})
    except AuthError as e:
        r = handle_auth_error(e)
        raise HTTPException(status_code=r["status_code"], detail=r["body"])


@router.post("/import")
def import_herbs(payload: dict, authorization: str = Header(default="")):
    """
    Corpo esperado: { "content": "<csv como string>" }
    """
    try:
        current_user = _get_current_user(authorization)
        require_role(current_user, ["ADMIN"])
        csv_content = payload.get("content", "")
        report = _service.import_from_csv(csv_content)
        return report
    except EmptyImportFile as e:
        raise HTTPException(status_code=400, detail={"error": "EMPTY_FILE", "message": str(e)})
    except AuthError as e:
        r = handle_auth_error(e)
        raise HTTPException(status_code=r["status_code"], detail=r["body"])
