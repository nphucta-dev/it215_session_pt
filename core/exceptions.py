from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from core.response import build_response


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=build_response(
                status_code=exc.status_code,
                data=None,
                message=str(exc.detail),
                path=request.url.path,
                error=exc.detail,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=build_response(
                status_code=422,
                data=None,
                message="Dữ liệu gửi lên không hợp lệ",
                path=request.url.path,
                error=exc.errors(),
            ),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        # Quy ước: mọi nơi bắt Exception chung phải re-raise HTTPException
        # trước, để không "nuốt" lỗi 401/403 thành 500.
        if isinstance(exc, HTTPException):
            raise exc
        return JSONResponse(
            status_code=500,
            content=build_response(
                status_code=500,
                data=None,
                message="Lỗi hệ thống",
                path=request.url.path,
                error=str(exc),
            ),
        )
