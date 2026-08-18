from datetime import datetime, timedelta, timezone

from jose import ExpiredSignatureError, JWTError, jwt

SECRET_KEY = "exam-authz-demo-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 20


def create_access_token(sub: str, role: str, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    # Không bắt Exception chung ở đây — để caller (middleware) phân biệt
    # rõ ExpiredSignatureError và JWTError để trả message phù hợp.
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


__all__ = ["create_access_token", "decode_token", "ExpiredSignatureError", "JWTError"]
