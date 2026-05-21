import json
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.prediction import (
    AnalyzeResponse,
    ClassProbability,
    DashboardAnalytics,
    PredictionDetail,
    PredictionSummary,
)
from app.services.prediction_service import (
    create_prediction,
    get_dashboard_stats,
    get_prediction,
    get_user_predictions,
)

router = APIRouter(prefix="/predictions", tags=["Predictions"])


def _file_url(user_id: int, filename: str) -> str:
    return f"/api/v1/files/{user_id}/{filename}"


def _to_summary(p, user_id: int) -> PredictionSummary:
    name = Path(p.image_path).name
    return PredictionSummary(
        id=p.id,
        diagnosis=p.diagnosis,
        confidence=p.confidence,
        image_url=_file_url(user_id, name),
        created_at=p.created_at,
    )


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_xray(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    settings = get_settings()
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    data = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File exceeds {settings.max_upload_mb}MB")

    try:
        record = create_prediction(db, current_user, data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc

    probs = json.loads(record.probabilities_json)
    grad_name = Path(record.grad_cam_path).name if record.grad_cam_path else None

    return AnalyzeResponse(
        id=record.id,
        diagnosis=record.diagnosis,
        confidence=record.confidence,
        probabilities=[ClassProbability(**p) for p in probs],
        ai_explanation=record.ai_explanation,
        grad_cam_url=_file_url(current_user.id, grad_name) if grad_name else None,
        image_url=_file_url(current_user.id, Path(record.image_path).name),
        created_at=record.created_at,
    )


@router.get("/history", response_model=list[PredictionSummary])
def history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = get_user_predictions(db, current_user.id)
    return [_to_summary(p, current_user.id) for p in rows]


@router.get("/dashboard", response_model=DashboardAnalytics)
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stats = get_dashboard_stats(db, current_user.id)
    return DashboardAnalytics(
        total_predictions=stats["total_predictions"],
        pneumonia_count=stats["pneumonia_count"],
        normal_count=stats["normal_count"],
        average_confidence=stats["average_confidence"],
        recent_predictions=[
            _to_summary(p, current_user.id) for p in stats["recent_predictions"]
        ],
        confidence_by_day=stats["confidence_by_day"],
    )


@router.get("/{prediction_id}", response_model=PredictionDetail)
def get_prediction_detail(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = get_prediction(db, current_user.id, prediction_id)
    if not record:
        raise HTTPException(status_code=404, detail="Prediction not found")

    probs = json.loads(record.probabilities_json)
    grad_name = Path(record.grad_cam_path).name if record.grad_cam_path else None

    return PredictionDetail(
        id=record.id,
        diagnosis=record.diagnosis,
        confidence=record.confidence,
        image_url=_file_url(current_user.id, Path(record.image_path).name),
        created_at=record.created_at,
        probabilities=[ClassProbability(**p) for p in probs],
        ai_explanation=record.ai_explanation,
        grad_cam_url=_file_url(current_user.id, grad_name) if grad_name else None,
        patient_note=record.patient_note,
    )
