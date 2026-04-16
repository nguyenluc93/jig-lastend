from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db
import models
from auth import hash_password, verify_password, create_access_token, require_admin
from schemas import LoginRequest
from routers import jigs, borrow, return_, comments, logs, admin

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="JIG Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Thu hẹp lại khi production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jigs.router)
app.include_router(borrow.router)
app.include_router(return_.router)
app.include_router(comments.router)
app.include_router(logs.router)
app.include_router(admin.router)

@app.post("/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(401, "Sai tài khoản hoặc mật khẩu")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "is_admin": user.is_admin}

@app.post("/auth/setup-admin")  # Chỉ dùng lần đầu, sau đó xóa
def setup_admin(db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == "admin").first()
    if existing:
        return {"msg": "Admin đã tồn tại"}
    admin_user = models.User(username="admin", hashed_password=hash_password("admin123"), is_admin=True)
    db.add(admin_user)
    db.commit()
    return {"msg": "Admin tạo thành công, đổi mật khẩu ngay!"}

@app.get("/")
def root():
    return {"status": "JIG API running"}