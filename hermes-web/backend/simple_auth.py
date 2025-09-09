"""
简化的认证端点 - 绕过数据库问题
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import jwt
import time

router = APIRouter(prefix="/simple-auth", tags=["simple-auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def simple_login(request: LoginRequest):
    """简化的登录端点"""
    # 简单的硬编码用户验证
    if request.username == "testuser" and request.password == "testpass":
        # 生成JWT token
        payload = {
            'sub': request.username,
            'exp': int(time.time()) + 3600  # 1小时后过期
        }
        token = jwt.encode(payload, 'your-secret-key-here', algorithm='HS256')
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "username": request.username,
                "email": "test@example.com"
            }
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

简化的认证端点 - 绕过数据库问题
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import jwt
import time

router = APIRouter(prefix="/simple-auth", tags=["simple-auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def simple_login(request: LoginRequest):
    """简化的登录端点"""
    # 简单的硬编码用户验证
    if request.username == "testuser" and request.password == "testpass":
        # 生成JWT token
        payload = {
            'sub': request.username,
            'exp': int(time.time()) + 3600  # 1小时后过期
        }
        token = jwt.encode(payload, 'your-secret-key-here', algorithm='HS256')
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "username": request.username,
                "email": "test@example.com"
            }
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
