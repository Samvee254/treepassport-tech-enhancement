from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.deps import require_role

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
    current_user: models.User = Depends(require_role("admin", "field_officer")),
):
    from app.audit import log_change

    tree = db.query(models.Tree).filter(models.Tree.id == tree_id).first()
    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")

    # capture the previous state BEFORE inserting the new record
    previous_record = (
        db.query(models.MonitoringRecord)
        .filter(models.MonitoringRecord.tree_id == tree_id)
        .order_by(models.MonitoringRecord.check_date.desc())
        .first()
    )
    previous_height = previous_record.height_cm if previous_record else None
    old_health_status = tree.current_health_status

    db_record = models.MonitoringRecord(tree_id=tree_id, **record.model_dump())
    db.add(db_record)

    # keep the cached snapshot on Tree in sync (per 05-database-design.md)
    tree.current_health_status = record.health_status

    db.flush()  # ensure db_record.id is populated before logging

    # Every monitoring insert produces an audit_logs entry, per
    # 05-database-design.md design notes. Not flagged unless it also
    # changed the parent tree's cached health status.
    log_change(
        db=db,
        tree_id=tree_id,
        user_id=current_user.id,
        field_changed="monitoring_record_added",
        old_value=f"height={previous_height}cm status={old_health_status}",
        new_value=f"height={record.height_cm}cm status={record.health_status}",
        action_type="create",
    )

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
