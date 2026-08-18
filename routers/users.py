from fastapi import APIRouter, Depends, HTTPException, Request

from core.response import build_response
from data.store import RESULTS_DB
from dependencies.auth import get_current_user, require_self_or_admin

router = APIRouter(tags=["users"])


@router.get("/users/{username}/results")
def get_user_results(
    username: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
    _owner_check: dict = Depends(require_self_or_admin),
):
    target = current_user["sub"] if username == "me" else username
    results = RESULTS_DB.get(target)
    if results is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy kết quả của người dùng này")
    return build_response(200, data=results, message="Kết quả thi", path=request.url.path)
