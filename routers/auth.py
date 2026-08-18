from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from core.response import build_response
from core.security import create_access_token
from data.store import USERS_DB

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(payload: LoginRequest, request: Request):
    user = USERS_DB.get(payload.username)
    if user is None or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Sai tên đăng nhập hoặc mật khẩu")
    token = create_access_token(sub=payload.username, role=user["role"])
    return build_response(200, data={"access_token": token, "token_type": "bearer"}, message="Đăng nhập thành công", path=request.url.path)
