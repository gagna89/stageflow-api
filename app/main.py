from fastapi import FastAPI

from app.core.config import settings
from app.api.routes import auth, users

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé."""
    return {"status": "healthy"}