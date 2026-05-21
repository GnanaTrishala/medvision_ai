from fastapi import APIRouter

from app.api.routes import auth, files, predictions, reports

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(predictions.router)
api_router.include_router(reports.router)
api_router.include_router(files.router)
