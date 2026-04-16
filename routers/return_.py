from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from routers.borrow import generate_qr_base64
import models, schemas
import secrets, os

router = APIRouter(prefix="/return", tags=["return"])
BASE_URL = os.getenv("FRONTEND_URL", "https://yourname.github.io/jig-app")

@router.get("/{session_token}", response_model=schemas.BorrowSessionOut)
def get_session(session_token: str, db: Session = Depends(get_db)):
    s = db.query(models.BorrowSession).filter(
        models.BorrowSession.session_token == session_token,
        models.BorrowSession.is_active == True
    ).first()
    if not s:
        raise HTTPException(404, "Session không tồn tại hoặc đã trả xong")
    return s

@router.post("/")
def return_jigs(req: schemas.ReturnRequest, db: Session = Depends(get_db)):
    session = db.query(models.BorrowSession).filter(
        models.BorrowSession.session_token == req.session_token,
        models.BorrowSession.is_active == True
    ).first()
    if not session:
        raise HTTPException(404, "Session không tìm thấy")

    all_jigs = session.jigs
    if req.jig_ids is None:
        # Trả toàn bộ
        returning = all_jigs
        remaining = []
    else:
        returning = [j for j in all_jigs if j.id in req.jig_ids]
        remaining = [j for j in all_jigs if j.id not in req.jig_ids]

    for jig in returning:
        jig.status = "available"

    log = models.Log(
        action="return",
        user_name=session.borrower_name,
        jig_names=", ".join(j.name for j in returning),
        session_token=session.session_token,
    )
    db.add(log)

    if remaining:
        # Tạo session mới cho phần còn lại
        new_token = secrets.token_urlsafe(32)
        new_qr = generate_qr_base64(f"{BASE_URL}/#/return?session={new_token}")
        new_session = models.BorrowSession(
            session_token=new_token,
            session_qr_url=new_qr,
            borrower_name=session.borrower_name,
        )
        new_session.jigs = remaining
        db.add(new_session)
        session.is_active = False
        db.commit()
        db.refresh(new_session)
        return {"status": "partial", "new_session_token": new_token, "new_session_qr_url": new_qr}
    else:
        session.is_active = False
        db.commit()
        return {"status": "complete"}