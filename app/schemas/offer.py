from pydantic import BaseModel, Field
from app.models.offer import OfferStatus
import datetime


# ---- Schéma de CREATION (POST) ----
class OfferCreate(BaseModel):
    title: str | None = Field(None, min_length=2, max_length=200)
    mission: str | None = None
    skills: str | None = None


# ---- Schéma de MISE A JOUR (PATCH) ----
class OfferUpdate(BaseModel):
    title: str | None = Field(None, min_length=2, max_length=200)
    mission: str | None = None
    skills: str | None = None


# ---- Décision du responsable pédagogique (review) ----
class OfferReviewDecision(BaseModel):
    decision: str = Field(pattern=r"^(publish|reject)$")


# ---- Schéma de RÉPONSE (GET) ----
class OfferResponse(BaseModel):
    id: int
    title: str | None
    mission: str | None
    skills: str | None
    status: OfferStatus
    company_id: int
    created_at: datetime.datetime

    model_config = {"from_attributes": True}