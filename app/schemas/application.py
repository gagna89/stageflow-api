from pydantic import BaseModel, Field
from app.models.application import ApplicationStatus
import datetime


# ---- Schéma de CREATION (POST) ----
class ApplicationCreate(BaseModel):
    pass  # rien à fournir : offer_id vient de l'URL, student_id du token JWT


# ---- Décision du responsable pédagogique ----
class ApplicationDecision(BaseModel):
    decision: str = Field(pattern=r"^(accepted|rejected)$")


# ---- Schéma de RÉPONSE (GET) ----
class ApplicationResponse(BaseModel):
    id: int
    status: ApplicationStatus
    student_id: int
    offer_id: int
    created_at: datetime.datetime

    model_config = {"from_attributes": True}