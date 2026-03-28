from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.freelancers import router as freelancers_router
from app.api.v1.matching import router as matching_router
from app.api.v1.parsing import router as parsing_router
from app.api.v1.projects import router as projects_router
from app.config import settings
from app.db.client import connect_to_mongo, disconnect_mongo, get_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    connect_to_mongo()
    yield
    disconnect_mongo()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allow_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    db = get_database()
    await db.command("ping")
    return {"status": "ok"}


app.include_router(freelancers_router, prefix=settings.api_prefix, tags=["freelancers"])
app.include_router(projects_router, prefix=settings.api_prefix, tags=["projects"])
app.include_router(parsing_router, prefix=settings.api_prefix, tags=["parsing"])
app.include_router(matching_router, prefix=settings.api_prefix, tags=["matching"])
