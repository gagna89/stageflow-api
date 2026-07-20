from fastapi import APIRouter
from app.core.security import CurrentUser
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser):
    """Retourne les informations de l'utilisateur connecté."""
    return current_user