from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.exceptions import register_exception_handlers
from middleware.auth_middleware import AuthMiddleware
from routers import admin, auth, exams, health, users

app = FastAPI(title="Exam Authorization Demo")

# CORS phải đứng trước AuthMiddleware trong ngăn xếp middleware để
# preflight OPTIONS được CORSMiddleware trả lời trước khi chạm AuthMiddleware.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)

register_exception_handlers(app)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(exams.router)
app.include_router(users.router)
app.include_router(admin.router)
