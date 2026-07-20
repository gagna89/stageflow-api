from fastapi import HTTPException, status
from app.models.role import RoleEnum
from app.models.user import User


def require_role(user: User, *allowed_roles: RoleEnum) -> None:
    """Lève une 403 si l'utilisateur n'a pas l'un des rôles autorisés."""
    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits pour effectuer cette action",
        )


def require_owner_or_role(
    user: User, owner_id: int, *allowed_roles: RoleEnum
) -> None:
    """Autorise si l'utilisateur est le propriétaire de la ressource OU a un rôle autorisé."""
    if user.id == owner_id:
        return
    if user.role in allowed_roles:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Vous n'avez pas les droits pour effectuer cette action",
    )
    