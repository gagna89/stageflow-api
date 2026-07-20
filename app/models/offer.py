from sqlalchemy import String, Text, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import datetime
import enum


class OfferStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    published = "published"
    rejected = "rejected"


class Offer(Base):
    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    mission: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[OfferStatus] = mapped_column(
        Enum(OfferStatus), default=OfferStatus.draft
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow
    )

    # Clé étrangère vers l'entreprise (User avec role=company)
    company_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    applications: Mapped[list["Application"]] = relationship(
        back_populates="offer",
        cascade="all, delete-orphan",
        lazy="selectin",
    )