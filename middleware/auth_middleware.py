from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.response import build_response
from core.security import ExpiredSignatureError, JWTError, decode_token

# Middleware KHÔNG map route -> role (tránh Bẫy 1: so khớp path có
# path parameter). Nó chỉ giải mã token nếu có và gắn vào request.state.
# Việc quyết định endpoint nào cần quyền gì thuộc về Dependency,
# vì Dependency luôn nhận đúng path parameter từ FastAPI routing.
PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Bẫy 2: request OPTIONS (CORS preflight) không mang JWT.
        if request.method == "OPTIONS":
            return await call_next(request)

        if request.url.path in PUBLIC_PATHS:
            request.state.user = None
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            # Không có token: để Dependency ở endpoint quyết định có
            # bắt buộc đăng nhập hay không (endpoint công khai vẫn chạy được).
            request.state.user = None
            return await call_next(request)

        token = auth_header.removeprefix("Bearer ").strip()
        try:
            payload = decode_token(token)
        except ExpiredSignatureError:
            return JSONResponse(
                status_code=401,
                content=build_response(401, message="Token đã hết hạn", path=request.url.path, error="token_expired"),
            )
        except JWTError:
            return JSONResponse(
                status_code=401,
                content=build_response(401, message="Token không hợp lệ", path=request.url.path, error="invalid_token"),
            )

        request.state.user = payload
        return await call_next(request)
