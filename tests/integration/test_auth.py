import pytest


@pytest.mark.asyncio
async def test_register_creates_user(client):
    """Un nouvel utilisateur peut s'inscrire avec succès."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "etudiant1@example.com",
            "password": "motdepasse123",
            "full_name": "Jean Dupont",
            "role": "student",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "etudiant1@example.com"
    assert data["role"] == "student"
    assert "hashed_password" not in data  # le mot de passe ne doit jamais sortir


@pytest.mark.asyncio
async def test_register_duplicate_email_fails(client):
    """Un email déjà utilisé ne peut pas se réinscrire."""
    payload = {
        "email": "duplicate@example.com",
        "password": "motdepasse123",
        "full_name": "Jean Dupont",
        "role": "student",
    }
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client):
    """Un utilisateur inscrit peut se connecter et recevoir un token JWT."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login_test@example.com",
            "password": "motdepasse123",
            "full_name": "Jean Dupont",
            "role": "student",
        },
    )

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "login_test@example.com", "password": "motdepasse123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password_fails(client):
    """Un mauvais mot de passe est refusé (401)."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongpass@example.com",
            "password": "motdepasse123",
            "full_name": "Jean Dupont",
            "role": "student",
        },
    )

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "wrongpass@example.com", "password": "mauvais_mot_de_passe"},
    )

    assert response.status_code == 401