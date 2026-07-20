from pydantic import BaseModel, EmailStr
from app.models.role import RoleEnum
import datetime


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: RoleEnum
    is_active: bool
    created_at: datetime.datetime

    model_config = {"from_attributes": True}