import os

from fastapi import APIRouter, HTTPException

from greenherb.auth.repository import UserJsonRepository
from greenherb.auth.password_hasher import PasswordHasher
from greenherb.auth.jwt_provider import JwtProvider
from greenherb.auth.service import AuthService
from greenherb.auth.exceptions import AuthError, ValidationError
from greenherb.auth.error_handler import handle_auth_error

router = APIRouter(prefix="/auth", tags=["auth"])

repository = UserJsonRepository("data/users.json")
hasher = PasswordHasher()

_jwt_secret = os.environ.get("JWT_SECRET")
if not _jwt_secret:
    import warnings
    warnings.warn(
        "JWT_SECRET não configurado. A usar segredo padrão inseguro. Defina JWT_SECRET em produção.",
        RuntimeWarning,
        stacklevel=1,
    )
    _jwt_secret = "segredo-super-secreto"

jwt_provider = JwtProvider(secret=_jwt_secret)

service = AuthService(repository, hasher, jwt_provider)


@router.post("/login")
def login(payload: dict):
    try:
        if "email" not in payload or "password" not in payload:
            raise ValidationError("Email e password são obrigatórios")

        return service.login(payload["email"], payload["password"])

    except AuthError as error:
        response = handle_auth_error(error)

        raise HTTPException(
            status_code=response["status_code"],
            detail=response["body"]
        )


@router.post("/refresh")
def refresh(payload: dict):
    try:
        if "refresh_token" not in payload:
            raise ValidationError("Refresh token é obrigatório")

        return service.refresh_access_token(payload["refresh_token"])

    except AuthError as error:
        response = handle_auth_error(error)

        raise HTTPException(
            status_code=response["status_code"],
            detail=response["body"]
        )
