from fastapi import FastAPI

from app.core.config import settings
from app.api.routes import auth, users, offers, applications
from app.middlewares.request_id import RequestIDMiddleware
from app.middlewares.security_headers import SecurityHeadersMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
)

# Middlewares (l'ordre d'ajout compte : le dernier ajouté s'exécute en premier)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(offers.router, prefix=settings.API_V1_PREFIX)
app.include_router(applications.router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé."""
    return {"status": "healthy"}