from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/trees", tags=["monitoring"])


@router.post(
    "/{tree_id}/monitoring",
    response_model=schemas.MonitoringRecordOut,
    status_code=201,
)
def add_monitoring_record(
    tree_id: int,
    record: schemas.MonitoringRecordCreate,
    db: Session = Depends(get_db),
):
    tree = db.query(models.Tree).filter(models.Tree.id == tree_id).first()
    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")

    db_record = models.MonitoringRecord(tree_id=tree_id, **record.model_dump())
    db.add(db_record)

    # keep the cached snapshot on Tree in sync (per 05-database-design.md)
    tree.current_health_status = record.health_status

    db.commit()
    db.refresh(db_record)
    return db_record


@router.get(
    "/{tree_id}/monitoring",
    response_model=list[schemas.MonitoringRecordOut],
)
def get_monitoring_history(tree_id: int, db: Session = Depends(get_db)):
    tree = db.query(models.Tree).filter(models.Tree.id == tree_id).first()
    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")

    return (
        db.query(models.MonitoringRecord)
        .filter(models.MonitoringRecord.tree_id == tree_id)
        .order_by(models.MonitoringRecord.check_date)
        .all()
    )
