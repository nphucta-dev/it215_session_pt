from fastapi import APIRouter, Depends, HTTPException, Request

from core.response import build_response
from data.store import RESULTS_DB, create_exam, delete_exam, lock_exam
from dependencies.auth import require_role
from schemas.exam import ExamCreateRequest

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/exams", status_code=201)
def create_exam_endpoint(
    payload: ExamCreateRequest,
    request: Request,
    current_user: dict = Depends(require_role("admin")),
):
    exam = create_exam(payload.name)
    return build_response(201, data=exam, message="Tạo ca thi thành công", path=request.url.path)


# Bẫy 1: path có tham số động {exam_id}. Vì dùng Dependency (không so
# khớp chuỗi ở middleware), FastAPI tự parse đúng exam_id cho mọi giá trị.
@router.patch("/exams/{exam_id}/lock")
def lock_exam_endpoint(
    exam_id: int,
    request: Request,
    current_user: dict = Depends(require_role("admin")),
):
    exam = lock_exam(exam_id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy ca thi")
    return build_response(200, data=exam, message="Đã khóa ca thi", path=request.url.path)


@router.get("/results")
def get_all_results(request: Request, current_user: dict = Depends(require_role("admin"))):
    return build_response(200, data=RESULTS_DB, message="Toàn bộ kết quả thi", path=request.url.path)


# Bẫy 3: endpoint mới thêm sau này rất dễ quên gắn Depends(require_role).
# Ở đây khai báo tường minh để tránh lỗi đó.
@router.delete("/exams/{exam_id}")
def delete_exam_endpoint(
    exam_id: int,
    request: Request,
    current_user: dict = Depends(require_role("admin")),
):
    deleted = delete_exam(exam_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Không tìm thấy ca thi")
    return build_response(200, data=None, message="Đã xóa ca thi", path=request.url.path)
