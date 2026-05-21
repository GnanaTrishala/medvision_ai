import io
from datetime import UTC, datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.prediction import Prediction
from app.models.user import User


def generate_pdf_report(prediction: Prediction, user: User) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=48,
        leftMargin=48,
        topMargin=48,
        bottomMargin=48,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "MedTitle",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#0f766e"),
        spaceAfter=12,
    )
    body = styles["BodyText"]

    story = [
        Paragraph("MedVision AI — Skin Lesion Analysis Report", title_style),
        Paragraph(
            f"<b>Patient / Clinician:</b> {user.full_name}<br/>"
            f"<b>Email:</b> {user.email}<br/>"
            f"<b>Report ID:</b> MV-{prediction.id:06d}<br/>"
            f"<b>Generated:</b> {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}",
            body,
        ),
        Spacer(1, 0.25 * inch),
        Table(
            [
                ["Primary Finding", prediction.diagnosis.replace("_", " ")],
                ["Confidence", f"{prediction.confidence * 100:.1f}%"],
                ["Analysis Date", prediction.created_at.strftime("%Y-%m-%d %H:%M")],
            ],
            colWidths=[2.2 * inch, 4 * inch],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0fdfa")),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ]
            ),
        ),
        Spacer(1, 0.3 * inch),
        Paragraph("<b>AI Interpretation</b>", styles["Heading2"]),
        Paragraph(prediction.ai_explanation.replace("\n", "<br/>"), body),
        Spacer(1, 0.2 * inch),
        Paragraph(
            "<i>Disclaimer: For research and clinical decision support only. "
            "Not FDA-cleared as a medical device.</i>",
            body,
        ),
    ]

    if prediction.grad_cam_path:
        try:
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph("<b>Grad-CAM Explainability</b>", styles["Heading2"]))
            story.append(RLImage(prediction.grad_cam_path, width=4 * inch, height=4 * inch))
        except Exception:
            pass

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
