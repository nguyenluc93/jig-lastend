from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import require_admin
from routers.borrow import generate_qr_base64
import models, schemas
import os

router = APIRouter(prefix="/admin", tags=["admin"])
BASE_URL = os.getenv("FRONTEND_URL", "https://yourname.github.io/jig-app")

@router.post("/jigs", response_model=schemas.JIGOut)
def create_jig(req: schemas.JIGCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    jig = models.JIG(**req.model_dump())
    db.add(jig)
    db.flush()
    # Tạo QR cố định cho JIG
    jig.qr_code_url = generate_qr_base64(f"{BASE_URL}/#/borrow?jig={jig.id}")
    db.commit()
    db.refresh(jig)
    return jig

@router.put("/jigs/{jig_id}", response_model=schemas.JIGOut)
def update_jig(jig_id: int, req: schemas.JIGCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    jig = db.query(models.JIG).filter(models.JIG.id == jig_id).first()
    if not jig:
        raise HTTPException(404, "Không tìm thấy JIG")
    for k, v in req.model_dump().items():
        setattr(jig, k, v)
    db.commit()
    db.refresh(jig)
    return jig

@router.delete("/jigs/{jig_id}")
def delete_jig(jig_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    jig = db.query(models.JIG).filter(models.JIG.id == jig_id).first()
    if not jig:
        raise HTTPException(404)
    db.delete(jig)
    db.commit()
    return {"ok": True}

@router.put("/jigs/{jig_id}/status")
def update_status(jig_id: int, status: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    jig = db.query(models.JIG).filter(models.JIG.id == jig_id).first()
    if not jig:
        raise HTTPException(404)
    jig.status = status
    db.commit()
    return {"ok": True}

@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    c = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    db.delete(c)
    db.commit()
    return {"ok": True}