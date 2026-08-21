from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.deps import require_role

router = APIRouter(prefix="/species", tags=["species"])


@router.post("", response_model=schemas.SpeciesOut, status_code=201)
def create_species(
    species: schemas.SpeciesCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin", "field_officer")),
):
    db_species = models.Species(**species.model_dump())
    db.add(db_species)
    db.commit()
    db.refresh(db_species)
    return db_species


@router.get("", response_model=list[schemas.SpeciesOut])
def list_species(db: Session = Depends(get_db)):
    return db.query(models.Species).all()
