from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.application import Application, ApplicationStatus


class ApplicationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, application_id: int) -> Application | None:
        result = await self.db.execute(
            select(Application).where(Application.id == application_id)
        )
        return result.scalar_one_or_none()

    async def get_by_student(self, student_id: int) -> list[Application]:
        result = await self.db.execute(
            select(Application).where(Application.student_id == student_id)
        )
        return list(result.scalars().all())

    async def get_by_offer(self, offer_id: int) -> list[Application]:
        result = await self.db.execute(
            select(Application).where(Application.offer_id == offer_id)
        )
        return list(result.scalars().all())

    async def get_active_by_student_and_offer(
        self, student_id: int, offer_id: int
    ) -> Application | None:
        """Vérifie si l'étudiant a déjà une candidature active (non retirée/refusée) sur cette offre."""
        result = await self.db.execute(
            select(Application).where(
                Application.student_id == student_id,
                Application.offer_id == offer_id,
                Application.status.in_(
                    [ApplicationStatus.pending, ApplicationStatus.accepted]
                ),
            )
        )
        return result.scalar_one_or_none()

    async def create(self, application: Application) -> Application:
        self.db.add(application)
        await self.db.flush()
        await self.db.refresh(application)
        return application

    async def count_by_status(self) -> dict[str, int]:
        result = await self.db.execute(
            select(Application.status, func.count(Application.id)).group_by(
                Application.status
            )
        )
        return {status.value: count for status, count in result}