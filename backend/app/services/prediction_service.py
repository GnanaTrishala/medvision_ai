import json
import uuid
from pathlib import Path

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.ml.inference import run_inference
from app.models.prediction import Prediction
from app.models.user import User


def _ensure_dirs(user_id: int) -> Path:
    settings = get_settings()
    path = Path(settings.uploads_dir) / str(user_id)
    path.mkdir(parents=True, exist_ok=True)
    artifacts = Path(settings.artifacts_dir) / str(user_id)
    artifacts.mkdir(parents=True, exist_ok=True)
    return path


def create_prediction(db: Session, user: User, image_bytes: bytes) -> Prediction:
    result = run_inference(image_bytes)
    uid = uuid.uuid4().hex[:12]
    base = _ensure_dirs(user.id)

    image_path = base / f"{uid}_xray.png"
    grad_path = base / f"{uid}_gradcam.png"

    image_path.write_bytes(image_bytes)
    grad_path.write_bytes(result.grad_cam_png)

    record = Prediction(
        user_id=user.id,
        diagnosis=result.diagnosis,
        confidence=result.confidence,
        probabilities_json=json.dumps(result.probabilities),
        image_path=str(image_path),
        grad_cam_path=str(grad_path),
        ai_explanation=result.ai_explanation,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_user_predictions(db: Session, user_id: int, limit: int = 50) -> list[Prediction]:
    return (
        db.query(Prediction)
        .filter(Prediction.user_id == user_id)
        .order_by(desc(Prediction.created_at))
        .limit(limit)
        .all()
    )


def get_prediction(db: Session, user_id: int, prediction_id: int) -> Prediction | None:
    return (
        db.query(Prediction)
        .filter(Prediction.id == prediction_id, Prediction.user_id == user_id)
        .first()
    )


def get_dashboard_stats(db: Session, user_id: int) -> dict:
    rows = (
        db.query(Prediction)
        .filter(Prediction.user_id == user_id)
        .order_by(desc(Prediction.created_at))
        .all()
    )
    total = len(rows)
    pneumonia = sum(1 for r in rows if r.diagnosis.upper() == "PNEUMONIA")
    normal = sum(1 for r in rows if r.diagnosis.upper() == "NORMAL")
    avg_conf = sum(r.confidence for r in rows) / total if total else 0.0

    by_day: dict[str, list[float]] = {}
    for r in rows:
        day = r.created_at.strftime("%Y-%m-%d")
        by_day.setdefault(day, []).append(r.confidence)

    confidence_by_day = [
        {"date": day, "average_confidence": round(sum(vals) / len(vals), 4)}
        for day, vals in sorted(by_day.items())
    ][-14:]

    return {
        "total_predictions": total,
        "pneumonia_count": pneumonia,
        "normal_count": normal,
        "average_confidence": round(avg_conf, 4),
        "recent_predictions": rows[:8],
        "confidence_by_day": confidence_by_day,
    }
