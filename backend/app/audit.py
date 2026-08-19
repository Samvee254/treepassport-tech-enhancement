from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app import models

SENSITIVE_FIELDS = {"gps_lat", "gps_lng", "verification_status", "species_id"}


def log_change(
    db: Session,
    tree_id: int,
    user_id: int | None,
    field_changed: str,
    old_value,
    new_value,
    action_type: str = "update",
):
    flagged = field_changed in SENSITIVE_FIELDS
    entry = models.AuditLog(
        tree_id=tree_id,
        user_id=user_id,
        field_changed=field_changed,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
        timestamp=datetime.now(timezone.utc),
        action_type=action_type,
        flagged=flagged,
    )
    db.add(entry)
    return entry
