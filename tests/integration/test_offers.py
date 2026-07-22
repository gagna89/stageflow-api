import pytest


async def register_and_login(client, email: str, role: str) -> str:
    """Fonction utilitaire : inscrit un utilisateur et retourne son token JWT."""
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


@pytest.mark.asyncio
async def test_student_cannot_create_offer(client):
    """Un étudiant n'a pas le droit de créer une offre (403)."""
    token = await register_and_login(client, "student1@example.com", "student")

    response = await client.post(
        "/api/v1/offers/",
        json={"title": "Stage Data", "mission": "Analyse", "skills": "Python"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_company_can_create_offer(client):
    """Une entreprise peut créer une offre en brouillon."""
    token = await register_and_login(client, "company1@example.com", "company")

    response = await client.post(
        "/api/v1/offers/",
        json={"title": "Stage Data", "mission": "Analyse", "skills": "Python"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "draft"


@pytest.mark.asyncio
async def test_offer_cannot_be_published_if_incomplete(client):
    """Une offre sans titre/mission/skills ne peut pas être publiée (invariant métier)."""
    company_token = await register_and_login(client, "company2@example.com", "company")
    manager_token = await register_and_login(client, "manager1@example.com", "program_manager")

    create_resp = await client.post(
        "/api/v1/offers/",
        json={"title": "Stage incomplet"},
        headers={"Authorization": f"Bearer {company_token}"},
    )
    offer_id = create_resp.json()["id"]

    await client.patch(
        f"/api/v1/offers/{offer_id}/submit",
        headers={"Authorization": f"Bearer {company_token}"},
    )

    review_resp = await client.patch(
        f"/api/v1/offers/{offer_id}/review",
        json={"decision": "publish"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )

    assert review_resp.status_code == 400


@pytest.mark.asyncio
async def test_full_offer_publication_flow(client):
    """Parcours nominal complet : création -> soumission -> publication."""
    company_token = await register_and_login(client, "company3@example.com", "company")
    manager_token = await register_and_login(client, "manager2@example.com", "program_manager")

    create_resp = await client.post(
        "/api/v1/offers/",
        json={"title": "Stage complet", "mission": "Développement API", "skills": "FastAPI"},
        headers={"Authorization": f"Bearer {company_token}"},
    )
    offer_id = create_resp.json()["id"]
    assert create_resp.json()["status"] == "draft"

    submit_resp = await client.patch(
        f"/api/v1/offers/{offer_id}/submit",
        headers={"Authorization": f"Bearer {company_token}"},
    )
    assert submit_resp.json()["status"] == "submitted"

    review_resp = await client.patch(
        f"/api/v1/offers/{offer_id}/review",
        json={"decision": "publish"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert review_resp.status_code == 200
    assert review_resp.json()["status"] == "published"