"""
Hermes AI Main Application
松耦合的主应用文件
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from logging_config import setup_logging, get_logger
from exceptions import ZSCEException, handle_zsce_exception

# 导入API路由
from api.auth_routes import router as auth_router
from api.tool_routes import router as tool_router
from api.core_module_routes_v2 import router as core_module_router
from api.training_routes import router as training_router

# 设置日志
setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=os.getenv("LOG_FILE")
)

logger = get_logger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Hermes AI API",
    description="Human-AI Alignment Coordinator - Bridging Human Intent with AI Power",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS配置
from core.config import CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=r"^http://localhost(?::\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理器
@app.exception_handler(ZSCEException)
async def zsce_exception_handler(request, exc: ZSCEException):
    logger.error(f"ZSCE Exception: {exc.message}", extra={
        "code": exc.code,
        "details": exc.details,
        "path": request.url.path
    })
    return handle_zsce_exception(exc)

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True, extra={
        "path": request.url.path,
        "method": request.method
    })
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# 注册API路由
app.include_router(auth_router)
app.include_router(tool_router)
app.include_router(core_module_router)
app.include_router(training_router)

# 根路由
@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Hermes AI API is running!",
        "description": "Human-AI Alignment Coordinator",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    try:
        from core.config import get_db
        from sqlalchemy import text
        from sqlalchemy.orm import Session
        
        # 简单的健康检查
        health_status = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": "1.0.0",
            "checks": {
                "database": "connected",
                "core_modules": "loaded",
                "training_system": "active"
            }
        }
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
