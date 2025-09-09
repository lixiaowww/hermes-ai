"""
Core Configuration Module
松耦合的配置管理
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from fastapi.security import HTTPBearer

# 加载环境变量
load_dotenv()

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable must be set")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 安全配置
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# CORS配置
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
]

# 上下文管理配置
CONTEXT_BUDGET_MESSAGES = int(os.getenv("CONTEXT_BUDGET_MESSAGES", "50"))
CONTEXT_BUDGET_TOKENS = int(os.getenv("CONTEXT_BUDGET_TOKENS", "8000"))
AUTO_CURATE = os.getenv("AUTO_CURATE", "false").lower() == "true"

# 本地实现开关
USE_LOCAL_EMBEDDING = os.getenv("USE_LOCAL_EMBEDDING", "true").lower() == "true"
USE_LOCAL_SUMMARY = os.getenv("USE_LOCAL_SUMMARY", "true").lower() == "true"

# 宪法治理配置
CONSTITUTION_FORBIDDEN = set([s.strip() for s in os.getenv("CONSTITUTION_FORBIDDEN", "").split(",") if s.strip()])

def get_db():
    """数据库会话依赖"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
