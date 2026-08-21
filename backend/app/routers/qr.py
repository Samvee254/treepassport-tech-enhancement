import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import qrcode

from app.database import get_db
from app import models

router = APIRouter(prefix="/trees", tags=["qr"])

# In production this would be a real public frontend URL.
# For the prototype, the QR encodes a link to the tree's API record.
BASE_PASSPORT_URL = "http://127.0.0.1:8000/trees"


@router.get("/{tree_id}/qr")
def get_tree_qr(tree_id: int, db: Session = Depends(get_db)):
    tree = db.query(models.Tree).filter(models.Tree.id == tree_id).first()
    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")

    passport_url = f"{BASE_PASSPORT_URL}/{tree.id}"

    img = qrcode.make(passport_url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="image/png",
        headers={"Content-Disposition": f"inline; filename={tree.tree_code}_qr.png"},
    )
