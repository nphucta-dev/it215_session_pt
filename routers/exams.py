from fastapi import APIRouter, Depends, Request

from core.response import build_response
from data.store import EXAMS_DB
from dependencies.auth import require_role

router = APIRouter(tags=["exams"])


@router.get("/exams")
def list_exams(request: Request, current_user: dict = Depends(require_role("admin", "user"))):
    return build_response(200, data=list(EXAMS_DB.values()), message="Danh sách ca thi", path=request.url.path)
