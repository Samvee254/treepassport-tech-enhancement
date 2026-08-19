from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.deps import get_current_user

router = APIRouter(prefix="/trees", tags=["trees"])


@router.post("", response_model=schemas.TreeOut, status_code=201)
def create_tree(tree: schemas.TreeCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Tree).filter(
        models.Tree.tree_code == tree.tree_code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="tree_code already exists")

    db_tree = models.Tree(**tree.model_dump())
    db.add(db_tree)
    db.commit()
    db.refresh(db_tree)
    return db_tree


@router.get("", response_model=list[schemas.TreeOut])
def list_trees(db: Session = Depends(get_db)):
    return db.query(models.Tree).all()


@router.get("/{tree_id}", response_model=schemas.TreeOut)
def get_tree(tree_id: int, db: Session = Depends(get_db)):
    tree = db.query(models.Tree).filter(models.Tree.id == tree_id).first()
    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")
    return tree


@router.patch("/{tree_id}", response_model=schemas.TreeOut)
def update_tree(
    tree_id: int,
    updates: schemas.TreeUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    from app.audit import log_change

    if current_user.role not in ("admin", "field_officer"):
        raise HTTPException(status_code=403, detail="Not authorized to update trees")

    tree = db.query(models.Tree).filter(models.Tree.id == tree_id).first()
    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")

    update_data = updates.model_dump(exclude_unset=True)
    flagged_fields = []

    for field, new_value in update_data.items():
        old_value = getattr(tree, field)
        if old_value != new_value:
            entry = log_change(db, tree_id, current_user.id, field, old_value, new_value)
            if entry.flagged:
                flagged_fields.append(field)
            setattr(tree, field, new_value)

    db.commit()
    db.refresh(tree)
    return tree
