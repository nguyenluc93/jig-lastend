from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class JIGOut(BaseModel):
    id: int
    name: str
    description: str
    image_url: str
    qr_code_url: str
    status: str
    model_config = {"from_attributes": True}

class JIGCreate(BaseModel):
    name: str
    description: str = ""
    image_url: str = ""

class BorrowRequest(BaseModel):
    borrower_name: str
    jig_ids: List[int]

class BorrowSessionOut(BaseModel):
    session_token: str
    session_qr_url: str
    jigs: List[JIGOut]
    model_config = {"from_attributes": True}

class ReturnRequest(BaseModel):
    session_token: str
    jig_ids: Optional[List[int]] = None  # None = trả toàn bộ

class LogOut(BaseModel):
    id: int
    action: str
    user_name: str
    jig_names: str
    session_token: str
    timestamp: datetime
    model_config = {"from_attributes": True}

class CommentCreate(BaseModel):
    jig_id: Optional[int] = None
    author_name: str
    content: str

class CommentOut(BaseModel):
    id: int
    author_name: str
    content: str
    created_at: datetime
    jig: Optional[JIGOut] = None
    model_config = {"from_attributes": True}

class TokenData(BaseModel):
    username: str

class LoginRequest(BaseModel):
    username: str
    password: str