import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.database import init_db
from app.routers import auth, profile, home, training, match, community, academy, health
# 导入models以确保表定义被注册
from app import models  # noqa: F401
from pathlib import Path
import traceback

# 创建FastAPI应用
app = FastAPI(
    title="Soccer App API",
    description="足球应用后端API",
    version="1.0.0"
)

# 配置CORS（允许跨域）
# 注意：CORS中间件必须在路由注册之前添加
# 对于文件上传，需要特别处理CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# 配置静态文件服务（用于提供头像访问）
uploads_dir = Path(__file__).parent.parent / "uploads"
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# 注册路由
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(home.router)
app.include_router(training.router)
app.include_router(match.router)
app.include_router(community.router)
app.include_router(academy.router)
app.include_router(health.router)


@app.on_event("startup")
async def startup_event():
    """启动时初始化数据库"""
    init_db()
    print("数据库初始化完成")


@app.get("/")
def root():
    return {"message": "Soccer App API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


# 全局异常处理，确保错误响应也包含CORS头
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器，确保错误响应包含CORS头"""
    import traceback
    error_trace = traceback.format_exc()
    print(f"全局异常捕获: {error_trace}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "服务器内部错误"
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理器，确保错误响应包含CORS头"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器，确保错误响应包含CORS头"""
    return JSONResponse(
        status_code=422,
        content={"detail": "请求参数不符合要求"}
    )

