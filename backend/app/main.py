from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import Base, engine
from app.models import Email, EmailAnalysis  # noqa: F401
from app.routers import analysis, dev, emails

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(emails.router)
app.include_router(analysis.router)
app.include_router(dev.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": settings.app_name, "status": "running"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": settings.app_name}
