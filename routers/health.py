from fastapi import APIRouter, Request

from core.response import build_response

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(request: Request):
    return build_response(200, data={"status": "up"}, message="Hệ thống hoạt động bình thường", path=request.url.path)
