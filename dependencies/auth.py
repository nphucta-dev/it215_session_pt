from fastapi import Depends, HTTPException, Request


def get_current_user(request: Request) -> dict:
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập hoặc token không hợp lệ")
    return user


def require_role(*allowed_roles: str):
    def checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(status_code=403, detail="Không đủ quyền truy cập")
        return current_user

    return checker


def require_self_or_admin(username: str, current_user: dict = Depends(get_current_user)) -> dict:
    # Bẫy 4: kiểm tra role thôi chưa đủ, còn phải kiểm tra quyền sở hữu dữ liệu.
    target = "me" if username == "me" else username
    is_self = target == "me" or current_user.get("sub") == target
    is_admin = current_user.get("role") == "admin"
    if not is_self and not is_admin:
        raise HTTPException(status_code=403, detail="Không có quyền xem kết quả của người dùng khác")
    return current_user
