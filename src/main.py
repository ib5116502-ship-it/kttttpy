from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.core.config import settings
from src.routers import auth, bookings, rooms

app = FastAPI(
    title="Booking API (KT6)",
    version="1.0.0",
    description="FastAPI + PostgreSQL + SQLAlchemy + Alembic + JWT/RBAC + Celery + Redis",
)

app.state.limiter = auth.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(bookings.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}