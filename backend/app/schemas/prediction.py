from datetime import datetime

from pydantic import BaseModel, Field


class ClassProbability(BaseModel):
    label: str
    confidence: float


class AnalyzeResponse(BaseModel):
    id: int
    diagnosis: str
    confidence: float
    probabilities: list[ClassProbability]
    ai_explanation: str
    grad_cam_url: str | None
    image_url: str
    created_at: datetime


class PredictionSummary(BaseModel):
    id: int
    diagnosis: str
    confidence: float
    image_url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PredictionDetail(PredictionSummary):
    probabilities: list[ClassProbability]
    ai_explanation: str
    grad_cam_url: str | None
    patient_note: str | None = None


class DashboardAnalytics(BaseModel):
    total_predictions: int
    pneumonia_count: int
    normal_count: int
    average_confidence: float
    recent_predictions: list[PredictionSummary]
    confidence_by_day: list[dict[str, float | str]]
