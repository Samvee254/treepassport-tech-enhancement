from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

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
