from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.prediction_service import get_prediction
from app.services.report_service import generate_pdf_report

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/{prediction_id}/pdf")
def download_report(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = get_prediction(db, current_user.id, prediction_id)
    if not record:
        raise HTTPException(status_code=404, detail="Prediction not found")

    pdf_bytes = generate_pdf_report(record, current_user)
    filename = f"medvision-report-{prediction_id:06d}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
