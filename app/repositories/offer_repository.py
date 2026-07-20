from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.offer import Offer, OfferStatus


class OfferRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, offer_id: int) -> Offer | None:
        result = await self.db.execute(select(Offer).where(Offer.id == offer_id))
        return result.scalar_one_or_none()

    async def get_all(
        self, skip: int = 0, limit: int = 20, status: OfferStatus | None = None
    ) -> list[Offer]:
        query = select(Offer)
        if status:
            query = query.where(Offer.status == status)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_company(self, company_id: int) -> list[Offer]:
        result = await self.db.execute(
            select(Offer).where(Offer.company_id == company_id)
        )
        return list(result.scalars().all())

    async def create(self, offer: Offer) -> Offer:
        self.db.add(offer)
        await self.db.flush()
        await self.db.refresh(offer)
        return offer

    async def count_by_status(self) -> dict[str, int]:
        result = await self.db.execute(
            select(Offer.status, func.count(Offer.id)).group_by(Offer.status)
        )
        return {status.value: count for status, count in result}