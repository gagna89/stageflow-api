# StageFlow API

API de gestion des stages pour un Master DSIA — permet aux étudiants de postuler à des offres de stage, aux entreprises de publier des offres, et aux responsables pédagogiques de valider le tout.

## Stack technique

- Python 3.11 + FastAPI
- PostgreSQL + SQLAlchemy 2.0 (async)
- Alembic (migrations)
- JWT (authentification)
- Docker / Docker Compose
- Pytest (tests)

## Installation

### 1. Cloner le projet

```bash
git clone https://github.com/gagna89/stageflow-api.git
cd stageflow-api
```

### 2. Créer l'environnement virtuel

```bash
python -m venv venv
venv\Scripts\Activate.ps1        # Windows
source venv/bin/activate         # Linux/macOS
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Créer un fichier `.env` à la racine avec :
APP_NAME=StageFlow
DEBUG=true
DATABASE_URL=sqlite+aiosqlite:///./dev.db
SECRET_KEY=change-me-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_PREFIX=/api/v1

## Lancement en local (sans Docker)

```bash
# Appliquer les migrations
alembic upgrade head

# Lancer le serveur
uvicorn app.main:app --reload
```

L'API est disponible sur `http://localhost:8000`
Documentation interactive : `http://localhost:8000/docs`

## Lancement avec Docker (recommandé)

```bash
docker compose up --build
```

Cette commande lance automatiquement :
- L'API FastAPI (port 8000)
- Une base PostgreSQL (port 5432)
- Les migrations Alembic

## Lancer les tests

```bash
pytest -v
```

Avec le rapport de couverture :

```bash
pytest --cov=app --cov-report=term-missing
```

## Rôles utilisateurs

| Rôle | Droits |
|---|---|
| `student` | Consulte les offres publiées, postule, retire une candidature (si non acceptée) |
| `company` | Crée et soumet des offres, consulte les candidatures de ses propres offres |
| `program_manager` | Publie/refuse les offres, accepte/refuse les candidatures, consulte les statistiques |
| `admin` | Gère les comptes utilisateurs et les rôles |

## Principaux endpoints

- `POST /api/v1/auth/register` — Inscription
- `POST /api/v1/auth/login` — Connexion (retourne un token JWT)
- `GET /api/v1/users/me` — Profil de l'utilisateur connecté
- `POST /api/v1/offers` — Créer une offre (entreprise)
- `PATCH /api/v1/offers/{id}/submit` — Soumettre une offre
- `PATCH /api/v1/offers/{id}/review` — Publier/refuser une offre (responsable)
- `POST /api/v1/offers/{id}/applications` — Postuler à une offre (étudiant)
- `PATCH /api/v1/applications/{id}/decision` — Accepter/refuser une candidature

La liste complète des endpoints est disponible sur `/docs` une fois le serveur lancé.