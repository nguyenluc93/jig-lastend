from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(prefix="/comments", tags=["comments"])

@router.get("/", response_model=list[schemas.CommentOut])
def list_comments(db: Session = Depends(get_db)):
    return db.query(models.Comment).order_by(models.Comment.created_at.desc()).limit(50).all()

@router.post("/", response_model=schemas.CommentOut)
def create_comment(req: schemas.CommentCreate, db: Session = Depends(get_db)):
    c = models.Comment(**req.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c