from fastapi import APIRouter, HTTPException, status
from app.core.security import DBSession, CurrentUser
from app.core.permissions import require_role, require_owner_or_role
from app.repositories.application_repository import ApplicationRepository
from app.models.application import ApplicationStatus
from app.models.role import RoleEnum
from app.schemas.application import ApplicationDecision, ApplicationResponse

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("/me", response_model=list[ApplicationResponse])
async def list_my_applications(db: DBSession, current_user: CurrentUser):
    """L'étudiant consulte ses propres candidatures."""
    repo = ApplicationRepository(db)
    return await repo.get_by_student(current_user.id)


@router.patch("/{application_id}/decision", response_model=ApplicationResponse)
async def decide_application(
    application_id: int, data: ApplicationDecision, db: DBSession, current_user: CurrentUser
):
    """Le responsable pédagogique accepte ou refuse une candidature."""
    require_role(current_user, RoleEnum.program_manager)

    repo = ApplicationRepository(db)
    application = await repo.get_by_id(application_id)
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidature introuvable")

    if application.status != ApplicationStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seule une candidature en attente peut être décidée",
        )

    application.status = ApplicationStatus(data.decision)
    await db.flush()
    await db.refresh(application)
    return application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def withdraw_application(application_id: int, db: DBSession, current_user: CurrentUser):
    """L'étudiant retire sa candidature, sauf si elle est déjà acceptée."""
    repo = ApplicationRepository(db)
    application = await repo.get_by_id(application_id)
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidature introuvable")

    require_owner_or_role(current_user, application.student_id, RoleEnum.admin)

    if application.status == ApplicationStatus.accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Une candidature acceptée ne peut plus être retirée",
        )

    application.status = ApplicationStatus.withdrawn
    await db.flush()