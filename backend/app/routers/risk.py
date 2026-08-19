from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.risk_engine import compute_risk

router = APIRouter(prefix="/trees", tags=["risk"])


@router.get("/{tree_id}/risk")
def get_tree_risk(tree_id: int, db: Session = Depends(get_db)):
    tree = db.query(models.Tree).filter(models.Tree.id == tree_id).first()
    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")

    records = (
        db.query(models.MonitoringRecord)
        .filter(models.MonitoringRecord.tree_id == tree_id)
        .order_by(models.MonitoringRecord.check_date)
        .all()
    )

    result = compute_risk(tree, records)
    return {"tree_id": tree_id, "tree_code": tree.tree_code, **result}
