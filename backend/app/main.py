from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import init_db
from app.ml.model_loader import bundle


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    Path(settings.uploads_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.artifacts_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.model_path).parent.mkdir(parents=True, exist_ok=True)
    init_db()
    try:
        bundle.load()
    except Exception as exc:
        print(f"Model preload warning: {exc}")
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        description="AI-powered HAM10000 skin lesion analysis with explainable Grad-CAM",
        version="1.0.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
        ],
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router, prefix=settings.api_v1_prefix)

    @application.get("/health")
    def health():
        return {"status": "ok", "service": settings.app_name}

    return application


app = create_app()
