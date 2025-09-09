"""
Authentication Service
松耦合的认证服务
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt as PyJWT
from passlib.context import CryptContext
from typing import Dict, Any, Optional

from core.config import pwd_context, security, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, get_db
from models import User as ORMUser

# 模拟数据库（保持向后兼容）
users_db = []

class AuthService:
    """认证服务类"""
    
    def __init__(self):
        self.pwd_context = pwd_context
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """生成密码哈希"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = PyJWT.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> Dict[str, Any]:
        """获取当前用户"""
        try:
            payload = PyJWT.decode(credentials.credentials, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # 先查内存用户；若没有则回退查数据库
            user = next((u for u in users_db if u["username"] == username), None)
            if user is None:
                orm_user = db.query(ORMUser).filter(ORMUser.username == username).first()
                if orm_user is None:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                user = {
                    "id": orm_user.id,
                    "username": orm_user.username,
                    "email": orm_user.email,
                    "password_hash": orm_user.hashed_password,
                    "is_active": orm_user.is_active,
                    "created_at": orm_user.created_at,
                }
                users_db.append(user)
            return user
            
        except PyJWT.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except PyJWT.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

# 创建全局实例
auth_service = AuthService()

# 导出常用函数
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return auth_service.verify_password(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return auth_service.get_password_hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    return auth_service.create_access_token(data, expires_delta)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> Dict[str, Any]:
    return auth_service.get_current_user(credentials, db)
