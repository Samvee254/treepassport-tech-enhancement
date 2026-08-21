import csv
import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.database import get_db
from app import models
from app.risk_engine import compute_risk

router = APIRouter(prefix="/reports", tags=["reports"])


def _build_summary(db: Session) -> dict:
    trees = db.query(models.Tree).all()
    total = len(trees)
    verified = sum(1 for t in trees if t.verification_status == "verified")
    pending = total - verified

    health_counts = {"healthy": 0, "moderate": 0, "at_risk": 0}
    at_risk_ids = []

    for t in trees:
        health_counts[t.current_health_status] = health_counts.get(t.current_health_status, 0) + 1

        records = (
            db.query(models.MonitoringRecord)
            .filter(models.MonitoringRecord.tree_id == t.id)
            .order_by(models.MonitoringRecord.check_date)
            .all()
        )
        risk = compute_risk(t, records)
        if risk["bucket"] == "HIGH":
            at_risk_ids.append(t.tree_code)

    counties = {t.county for t in trees if t.county}
    survival_rate = round((health_counts.get("healthy", 0) + health_counts.get("moderate", 0)) / total * 100, 1) if total else 0.0

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "trees_registered": total,
        "verified": verified,
        "pending": pending,
        "health_status_healthy": health_counts.get("healthy", 0),
        "health_status_moderate": health_counts.get("moderate", 0),
        "health_status_at_risk": health_counts.get("at_risk", 0),
        "survival_rate_percent": survival_rate,
        "counties": sorted(counties),
        "risk_engine_high_bucket_tree_codes": at_risk_ids,
    }


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    return _build_summary(db)


@router.get("/export/csv")
def export_csv(db: Session = Depends(get_db)):
    trees = db.query(models.Tree).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "tree_code", "county", "gps_lat", "gps_lng", "planting_date",
        "verification_status", "current_health_status", "created_at"
    ])
    for t in trees:
        writer.writerow([
            t.tree_code, t.county, t.gps_lat, t.gps_lng, t.planting_date,
            t.verification_status, t.current_health_status, t.created_at
        ])

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=trees_export.csv"},
    )


@router.get("/export/pdf")
def export_pdf(db: Session = Depends(get_db)):
    summary = _build_summary(db)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 60
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "PROJECT IMPACT REPORT")
    y -= 30

    c.setFont("Helvetica", 11)
    lines = [
        f"Generated: {summary['generated_at']}",
        "",
        f"Trees registered: {summary['trees_registered']}",
        f"Verified: {summary['verified']}",
        f"Pending: {summary['pending']}",
        "",
        f"Health status (raw check-in): Healthy {summary['health_status_healthy']}, "
        f"Moderate {summary['health_status_moderate']}, At Risk {summary['health_status_at_risk']}",
        f"Survival rate: {summary['survival_rate_percent']}%",
        "",
        f"Counties: {', '.join(summary['counties']) or 'None recorded'}",
        "",
        "Risk Engine HIGH-bucket trees (computed score, not raw status):",
    ]
    for line in lines:
        c.drawString(50, y, line)
        y -= 18

    for code in summary["risk_engine_high_bucket_tree_codes"]:
        c.drawString(70, y, f"- {code}")
        y -= 16

    if not summary["risk_engine_high_bucket_tree_codes"]:
        c.drawString(70, y, "(none)")
        y -= 16

    c.showPage()
    c.save()
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=impact_report.pdf"},
    )
