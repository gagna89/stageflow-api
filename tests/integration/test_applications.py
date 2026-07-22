import pytest


async def register_and_login(client, email: str, role: str) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "motdepasse123",
            "full_name": "Test User",
            "role": role,
        },
    )
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "motdepasse123"},
    )
    return response.json()["access_token"]


async def create_and_publish_offer(client, company_token: str, manager_token: str) -> int:
    """Crée une offre complète, la soumet et la publie. Retourne son id."""
    create_resp = await client.post(
        "/api/v1/offers/",
        json={"title": "Stage Data", "mission": "Analyse de données", "skills": "Python, SQL"},
        headers={"Authorization": f"Bearer {company_token}"},
    )
    offer_id = create_resp.json()["id"]

    await client.patch(
        f"/api/v1/offers/{offer_id}/submit",
        headers={"Authorization": f"Bearer {company_token}"},
    )
    await client.patch(
        f"/api/v1/offers/{offer_id}/review",
        json={"decision": "publish"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    return offer_id


@pytest.mark.asyncio
async def test_student_can_apply_to_published_offer(client):
    """Un étudiant peut postuler à une offre publiée."""
    company_token = await register_and_login(client, "companyA@example.com", "company")
    manager_token = await register_and_login(client, "managerA@example.com", "program_manager")
    student_token = await register_and_login(client, "studentA@example.com", "student")

    offer_id = await create_and_publish_offer(client, company_token, manager_token)

    response = await client.post(
        f"/api/v1/offers/{offer_id}/applications",
        headers={"Authorization": f"Bearer {student_token}"},
    )

    assert response.status_code == 201
    assert response.json()["status"] == "pending"


@pytest.mark.asyncio
async def test_student_cannot_apply_twice_to_same_offer(client):
    """Un étudiant ne peut avoir qu'une seule candidature active par offre (invariant métier)."""
    company_token = await register_and_login(client, "companyB@example.com", "company")
    manager_token = await register_and_login(client, "managerB@example.com", "program_manager")
    student_token = await register_and_login(client, "studentB@example.com", "student")

    offer_id = await create_and_publish_offer(client, company_token, manager_token)

    await client.post(
        f"/api/v1/offers/{offer_id}/applications",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    second_response = await client.post(
        f"/api/v1/offers/{offer_id}/applications",
        headers={"Authorization": f"Bearer {student_token}"},
    )

    assert second_response.status_code == 400


@pytest.mark.asyncio
async def test_company_cannot_see_applications_of_another_company_offer(client):
    """
    TEST D'ISOLATION EXPLICITEMENT DEMANDÉ PAR LE SUJET :
    une entreprise ne doit jamais pouvoir consulter les candidatures
    d'une offre appartenant à une autre entreprise.
    """
    company_a_token = await register_and_login(client, "companyC@example.com", "company")
    company_b_token = await register_and_login(client, "companyD@example.com", "company")
    manager_token = await register_and_login(client, "managerC@example.com", "program_manager")
    student_token = await register_and_login(client, "studentC@example.com", "student")

    offer_id = await create_and_publish_offer(client, company_a_token, manager_token)

    await client.post(
        f"/api/v1/offers/{offer_id}/applications",
        headers={"Authorization": f"Bearer {student_token}"},
    )

    response = await client.get(
        f"/api/v1/offers/{offer_id}/applications",
        headers={"Authorization": f"Bearer {company_b_token}"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_accepted_application_cannot_be_withdrawn(client):
    """Une candidature acceptée ne peut plus être retirée par l'étudiant (invariant métier)."""
    company_token = await register_and_login(client, "companyE@example.com", "company")
    manager_token = await register_and_login(client, "managerE@example.com", "program_manager")
    student_token = await register_and_login(client, "studentE@example.com", "student")

    offer_id = await create_and_publish_offer(client, company_token, manager_token)

    apply_resp = await client.post(
        f"/api/v1/offers/{offer_id}/applications",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    application_id = apply_resp.json()["id"]

    await client.patch(
        f"/api/v1/applications/{application_id}/decision",
        json={"decision": "accepted"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )

    withdraw_resp = await client.delete(
        f"/api/v1/applications/{application_id}",
        headers={"Authorization": f"Bearer {student_token}"},
    )

    assert withdraw_resp.status_code == 400