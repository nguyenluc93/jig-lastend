from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
import secrets, qrcode, base64
from io import BytesIO
import os

router = APIRouter(prefix="/borrow", tags=["borrow"])

BASE_URL = os.getenv("FRONTEND_URL", "https://nguyenluc93.github.io/jig-lastend")

def generate_qr_base64(data: str) -> str:
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

@router.post("/", response_model=schemas.BorrowSessionOut)
def borrow(req: schemas.BorrowRequest, db: Session = Depends(get_db)):
    jigs = db.query(models.JIG).filter(
        models.JIG.id.in_(req.jig_ids),
        models.JIG.status == "available"
    ).all()
    if len(jigs) != len(req.jig_ids):
        raise HTTPException(400, "Một số JIG không có sẵn hoặc không tồn tại")

    token = secrets.token_urlsafe(32)
    return_url = f"{BASE_URL}/#/return?session={token}"
    session_qr = generate_qr_base64(return_url)

    session = models.BorrowSession(
        session_token=token,
        session_qr_url=session_qr,
        borrower_name=req.borrower_name,
    )
    session.jigs = jigs
    for jig in jigs:
        jig.status = "in_use"

    log = models.Log(
        action="borrow",
        user_name=req.borrower_name,
        jig_names=", ".join(j.name for j in jigs),
        session_token=token,
    )
    db.add(session)
    db.add(log)
    db.commit()
    db.refresh(session)
    return session