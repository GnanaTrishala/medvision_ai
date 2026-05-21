from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    diagnosis: Mapped[str] = mapped_column(String(100))
    confidence: Mapped[float] = mapped_column(Float)
    probabilities_json: Mapped[str] = mapped_column(Text)

    image_path: Mapped[str] = mapped_column(String(500))
    grad_cam_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    ai_explanation: Mapped[str] = mapped_column(Text)
    patient_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True
    )

    user: Mapped["User"] = relationship(back_populates="predictions")


from app.models.user import User  # noqa: E402
