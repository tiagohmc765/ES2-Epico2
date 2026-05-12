import os

from fastapi import APIRouter, HTTPException, Header

from greenherb.auth.repository import UserJsonRepository
from greenherb.auth.password_hasher import PasswordHasher
from greenherb.auth.jwt_provider import JwtProvider
from greenherb.auth.access_control import require_role
from greenherb.auth.exceptions import AuthError, ValidationError, AccessDenied
from greenherb.auth.error_handler import handle_auth_error

router = APIRouter(prefix="/users", tags=["users"])

repository = UserJsonRepository("data/users.json")
hasher = PasswordHasher()

_jwt_secret = os.environ.get("JWT_SECRET", "segredo-super-secreto")
jwt_provider = JwtProvider(secret=_jwt_secret)

VALID_ROLES = {"ADMIN", "RESPONSAVEL", "TECNICO"}


def _get_current_user(authorization: str) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise AccessDenied("Token ausente ou inválido")
    token = authorization[len("Bearer "):]
    return jwt_provider.decode(token)


@router.get("")
def list_users(authorization: str = Header(default="")):
    try:
        current_user = _get_current_user(authorization)
        require_role(current_user, ["ADMIN"])
        users = repository.list_all()
        return [{"id": u["id"], "email": u["email"], "role": u["role"]} for u in users]
    except AuthError as error:
        response = handle_auth_error(error)
        raise HTTPException(status_code=response["status_code"], detail=response["body"])


@router.post("", status_code=201)
def create_user(payload: dict, authorization: str = Header(default="")):
    try:
        current_user = _get_current_user(authorization)
        require_role(current_user, ["ADMIN"])

        if not all(k in payload for k in ("email", "password", "role")):
            raise ValidationError("email, password e role são obrigatórios")

        if payload["role"] not in VALID_ROLES:
            raise ValidationError(f"role inválido. Valores válidos: {', '.join(sorted(VALID_ROLES))}")

        if repository.find_by_email(payload["email"]) is not None:
            raise ValidationError("Email já registado")

        all_users = repository.list_all()
        new_id = max((u["id"] for u in all_users), default=0) + 1

        new_user = {
            "id": new_id,
            "email": payload["email"],
            "password_hash": hasher.hash(payload["password"]),
            "role": payload["role"],
        }

        repository.save(new_user)
        return {"id": new_user["id"], "email": new_user["email"], "role": new_user["role"]}
    except AuthError as error:
        response = handle_auth_error(error)
        raise HTTPException(status_code=response["status_code"], detail=response["body"])


@router.get("/{user_id}")
def get_user(user_id: int, authorization: str = Header(default="")):
    try:
        current_user = _get_current_user(authorization)
        require_role(current_user, ["ADMIN"])
        user = repository.find_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=404,
                detail={"error": "NOT_FOUND", "message": "Utilizador não encontrado"},
            )
        return {"id": user["id"], "email": user["email"], "role": user["role"]}
    except AuthError as error:
        response = handle_auth_error(error)
        raise HTTPException(status_code=response["status_code"], detail=response["body"])


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, authorization: str = Header(default="")):
    try:
        current_user = _get_current_user(authorization)
        require_role(current_user, ["ADMIN"])
        if not repository.delete_by_id(user_id):
            raise HTTPException(
                status_code=404,
                detail={"error": "NOT_FOUND", "message": "Utilizador não encontrado"},
            )
        return None
    except AuthError as error:
        response = handle_auth_error(error)
        raise HTTPException(status_code=response["status_code"], detail=response["body"])
