from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.deps import require_role

router = APIRouter(prefix="/trees", tags=["audit"])


@router.get("/{tree_id}/audit")
def get_audit_log(
    tree_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin", "field_officer")),
):
    tree = db.query(models.Tree).filter(models.Tree.id == tree_id).first()
    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")

    logs = (
        db.query(models.AuditLog)
        .filter(models.AuditLog.tree_id == tree_id)
        .order_by(models.AuditLog.timestamp)
        .all()
    )
    return [
        {
            "id": l.id,
            "user_id": l.user_id,
            "field_changed": l.field_changed,
            "old_value": l.old_value,
            "new_value": l.new_value,
            "timestamp": l.timestamp,
            "action_type": l.action_type,
            "flagged": l.flagged,
        }
        for l in logs
    ]
