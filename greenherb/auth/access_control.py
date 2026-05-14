from greenherb.auth.exceptions import AccessDenied


def require_role(user: dict, allowed_roles: list[str]) -> bool:
    if user is None:
        raise AccessDenied("Utilizador não autenticado")

    if user.get("role") not in allowed_roles:
        raise AccessDenied("Permissão negada")

    return True
