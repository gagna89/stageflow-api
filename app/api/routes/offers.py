from fastapi import APIRouter, HTTPException, status
from app.core.security import DBSession, CurrentUser
from app.core.permissions import require_role, require_owner_or_role
from app.repositories.offer_repository import OfferRepository
from app.repositories.application_repository import ApplicationRepository
from app.models.offer import Offer, OfferStatus
from app.models.application import Application, ApplicationStatus
from app.models.role import RoleEnum
from app.schemas.offer import OfferCreate, OfferUpdate, OfferReviewDecision, OfferResponse
from app.schemas.application import ApplicationResponse

router = APIRouter(prefix="/offers", tags=["Offers"])


@router.post("/", response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
async def create_offer(data: OfferCreate, db: DBSession, current_user: CurrentUser):
    """Une entreprise crée une offre en brouillon."""
    require_role(current_user, RoleEnum.company)

    offer = Offer(
        title=data.title,
        mission=data.mission,
        skills=data.skills,
        company_id=current_user.id,
        status=OfferStatus.draft,
    )
    repo = OfferRepository(db)
    return await repo.create(offer)


@router.get("/", response_model=list[OfferResponse])
async def list_offers(
    db: DBSession,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 20,
):
    """Un étudiant voit les offres publiées ; une entreprise voit les siennes."""
    repo = OfferRepository(db)

    if current_user.role == RoleEnum.company:
        return await repo.get_by_company(current_user.id)

    return await repo.get_all(skip=skip, limit=limit, status=OfferStatus.published)


@router.get("/{offer_id}", response_model=OfferResponse)
async def get_offer(offer_id: int, db: DBSession, current_user: CurrentUser):
    repo = OfferRepository(db)
    offer = await repo.get_by_id(offer_id)
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offre introuvable")

    if offer.status != OfferStatus.published:
        require_owner_or_role(
            current_user, offer.company_id, RoleEnum.program_manager, RoleEnum.admin
        )

    return offer


@router.patch("/{offer_id}/submit", response_model=OfferResponse)
async def submit_offer(offer_id: int, db: DBSession, current_user: CurrentUser):
    """L'entreprise soumet son offre en brouillon pour validation."""
    repo = OfferRepository(db)
    offer = await repo.get_by_id(offer_id)
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offre introuvable")

    require_owner_or_role(current_user, offer.company_id, RoleEnum.admin)

    if offer.status != OfferStatus.draft:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seule une offre en brouillon peut être soumise",
        )

    offer.status = OfferStatus.submitted
    await db.flush()
    await db.refresh(offer)
    return offer


@router.patch("/{offer_id}/review", response_model=OfferResponse)
async def review_offer(
    offer_id: int, data: OfferReviewDecision, db: DBSession, current_user: CurrentUser
):
    """Le responsable pédagogique publie ou refuse une offre soumise."""
    require_role(current_user, RoleEnum.program_manager)

    repo = OfferRepository(db)
    offer = await repo.get_by_id(offer_id)
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offre introuvable")

    if offer.status != OfferStatus.submitted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seule une offre soumise peut être validée ou refusée",
        )

    if data.decision == "publish":
        if not (offer.title and offer.mission and offer.skills and offer.company_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'offre doit avoir titre, mission, compétences et entreprise pour être publiée",
            )
        offer.status = OfferStatus.published
    else:
        offer.status = OfferStatus.rejected

    await db.flush()
    await db.refresh(offer)
    return offer


@router.post(
    "/{offer_id}/applications",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def apply_to_offer(offer_id: int, db: DBSession, current_user: CurrentUser):
    """Un étudiant postule à une offre publiée."""
    require_role(current_user, RoleEnum.student)

    offer_repo = OfferRepository(db)
    offer = await offer_repo.get_by_id(offer_id)
    if not offer or offer.status != OfferStatus.published:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offre introuvable")

    app_repo = ApplicationRepository(db)
    existing = await app_repo.get_active_by_student_and_offer(current_user.id, offer_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous avez déjà une candidature active sur cette offre",
        )

    application = Application(
        student_id=current_user.id,
        offer_id=offer_id,
        status=ApplicationStatus.pending,
    )
    return await app_repo.create(application)


@router.get("/{offer_id}/applications", response_model=list[ApplicationResponse])
async def list_offer_applications(offer_id: int, db: DBSession, current_user: CurrentUser):
    """L'entreprise voit les candidatures de sa propre offre uniquement."""
    offer_repo = OfferRepository(db)
    offer = await offer_repo.get_by_id(offer_id)
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offre introuvable")

    require_owner_or_role(
        current_user, offer.company_id, RoleEnum.program_manager, RoleEnum.admin
    )

    app_repo = ApplicationRepository(db)
    return await app_repo.get_by_offer(offer_id)