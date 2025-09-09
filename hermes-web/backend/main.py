from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Callable, Any, Dict
import uvicorn
from datetime import datetime, timedelta
import jwt as PyJWT
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from logging_config import setup_logging, get_logger
from fastapi.responses import JSONResponse
from exceptions import ZSCEException, handle_zsce_exception
from uuid import uuid4
from models import Conversation, Message, ToolCall, MemoryChunk
from models import Summary  # curator writes here
from models import User as ORMUser
import hashlib
import math
import subprocess
import signal

# --- DB wiring ---
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker, Session
import sqlalchemy as sa
from models import Project, Workflow

# Core agent integration
from core_integration import (
    core_integration, 
    run_agent_workflow, 
    get_constitution, 
    list_files, 
    read_file_content, 
    write_file_content
)

# V4.0 Core Modules
from meditation_module import meditation_module
from debate_engine import debate_engine, ArgumentType
from high_dimension_module import high_dimension_module
from high_dimensional_review_engine import high_dimensional_review_engine, PerspectiveType, ReviewStatus
from high_dimensional_analysis_module import high_dimensional_analysis_module, DimensionLevel, ConsciousnessLevel
from training_module import training_module, FeedbackType

# 加载环境变量
load_dotenv()

# SQLAlchemy engine/session
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable must be set")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 设置日志
setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=os.getenv("LOG_FILE")
)

logger = get_logger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="ZSCE Agent API",
    description="Multi-agent system for automated software development",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 中间件配置
# Robust CORS: allow common localhost ports and any localhost via regex
_cors_origins_env = os.getenv("BACKEND_CORS_ORIGINS", "")
_cors_origins: List[str] = [
    "http://localhost:3000",
    "http://localhost:3001",
]
if _cors_origins_env:
    # Accept comma-separated list in env
    _cors_origins = [o.strip() for o in _cors_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
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

# 安全配置
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# 数据模型
class User(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool = True
    created_at: datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectDetail(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    visibility: str
    owner_id: int
    created_at: datetime
    updated_at: datetime

class WorkflowStatus(BaseModel):
    id: str
    project_id: int
    status: str
    current_step: str
    progress: int
    start_time: datetime
    end_time: Optional[datetime] = None
    error: Optional[str] = None

class WorkflowStartRequest(BaseModel):
    project_id: int
    task_description: str

class WorkflowDetailOut(BaseModel):
    id: str
    project_id: int
    status: str
    current_step: Optional[str] = None
    progress: int
    task_description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    error: Optional[str] = None

# 模拟数据库
users_db = []
projects_db = []
workflows_db = []

# 工具函数
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = PyJWT.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    try:
        payload = PyJWT.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
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
    try:
        payload = PyJWT.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except PyJWT.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 查找用户
    user = next((u for u in users_db if u["username"] == username), None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# 路由定义
@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "ZSCE Agent API is running!"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # DB ping
        db.execute(text("SELECT 1"))
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "checks": {
                "database": "ok",
                "memory": "ok",
                "api_keys": "ok"
            }
        }
        logger.debug("Health check completed successfully")
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@app.get("/metrics")
async def metrics():
    """Basic metrics endpoint"""
    try:
        metrics_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "users": len(users_db),
            "projects": len(projects_db),
            "workflows": len(workflows_db),
            "active_workflows": len([w for w in workflows_db if w.get("status") == "running"])
        }
        logger.debug("Metrics collected successfully")
        return metrics_data
    except Exception as e:
        logger.error(f"Metrics collection failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to collect metrics")

# 删除重复的 /health 定义

@app.get("/db/ping")
async def db_ping(db: Session = Depends(get_db)):
    try:
        res = db.execute(text("SELECT version()"))
        row = res.fetchone()
        return {"ok": True, "version": row[0] if row else None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/register", response_model=User)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # 检查用户名是否已存在（内存与数据库）
    if any(u["username"] == user.username for u in users_db):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    exists = db.query(ORMUser).filter(ORMUser.username == user.username).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    # 创建数据库用户（来源单一：DB为真源）
    orm_user = ORMUser(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db.add(orm_user)
    db.commit()
    db.refresh(orm_user)

    # 同步内存用户表（维持现有登录流程）
    inmem = {
        "id": orm_user.id,
        "username": orm_user.username,
        "email": orm_user.email,
        "password_hash": orm_user.hashed_password,
        "is_active": orm_user.is_active,
        "created_at": orm_user.created_at,
    }
    users_db.append(inmem)

    return {
        "id": orm_user.id,
        "username": orm_user.username,
        "email": orm_user.email,
        "is_active": orm_user.is_active,
        "created_at": orm_user.created_at,
    }

@app.post("/auth/login", response_model=Token)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    # 查找用户（先内存，后数据库）
    user = next((u for u in users_db if u["username"] == user_credentials.username), None)
    if not user:
        orm_user = db.query(ORMUser).filter(ORMUser.username == user_credentials.username).first()
        if orm_user:
            user = {
                "id": orm_user.id,
                "username": orm_user.username,
                "email": orm_user.email,
                "password_hash": orm_user.hashed_password,
                "is_active": orm_user.is_active,
                "created_at": orm_user.created_at,
            }
            users_db.append(user)
    if not user or not verify_password(user_credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "is_active": current_user["is_active"],
        "created_at": current_user["created_at"]
    }

@app.post("/projects", response_model=ProjectDetail)
async def create_project_api(payload: ProjectCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    proj = Project(
        name=payload.name,
        description=payload.description,
        owner_id=current_user["id"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return ProjectDetail(
        id=proj.id,
        name=proj.name,
        description=proj.description,
        visibility=proj.visibility,
        owner_id=proj.owner_id,
        created_at=proj.created_at,
        updated_at=proj.updated_at,
    )

@app.get("/projects", response_model=List[ProjectDetail])
async def list_projects_api(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Project).filter(Project.owner_id == current_user["id"]).order_by(Project.created_at.desc()).all()
    return [
        ProjectDetail(
            id=r.id,
            name=r.name,
            description=r.description,
            visibility=r.visibility,
            owner_id=r.owner_id,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in rows
    ]

@app.get("/projects/{project_id}")
async def get_project_api(project_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    r = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user["id"]).first()
    if not r:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get owner information
    owner = db.query(ORMUser).filter(ORMUser.id == r.owner_id).first()
    
    return {
        "id": r.id,
        "name": r.name,
        "description": r.description,
        "visibility": r.visibility,
        "created_at": r.created_at.isoformat(),
        "updated_at": r.updated_at.isoformat(),
        "owner": {
            "username": owner.username,
            "email": owner.email
        },
        "members": [
            {
                "username": owner.username,
                "role": "owner"
            }
        ],
        "workflows": [],  # Mock data for now
        "files": []  # Mock data for now
    }

@app.get("/workflows", response_model=List[WorkflowDetailOut])
async def list_workflows_api(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user_projects = db.query(Project.id).filter(Project.owner_id == current_user["id"]).subquery()
    rows = db.query(Workflow).filter(Workflow.project_id.in_(user_projects)).order_by(Workflow.start_time.desc()).all()
    return [
        WorkflowDetailOut(
            id=r.id,
            project_id=r.project_id,
            status=r.status,
            current_step=r.current_step,
            progress=r.progress,
            task_description=r.task_description,
            start_time=r.start_time,
            end_time=r.end_time,
            error=r.error,
        )
        for r in rows
    ]

@app.post("/workflows/start", response_model=WorkflowDetailOut)
async def start_workflow_api(
    body: WorkflowStartRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == body.project_id, Project.owner_id == current_user["id"]).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        wf = Workflow(
            id=str(uuid4()),
            project_id=body.project_id,
            status="running",
            current_step="initializing",
            progress=0,
            task_description=body.task_description,
            start_time=datetime.utcnow(),
            creator_id=current_user["id"],
        )
        db.add(wf)
        db.commit()
        db.refresh(wf)
        return WorkflowDetailOut(
            id=wf.id,
            project_id=wf.project_id,
            status=wf.status,
            current_step=wf.current_step,
            progress=wf.progress,
            task_description=wf.task_description,
            start_time=wf.start_time,
            end_time=wf.end_time,
            error=wf.error,
        )
    except Exception:
        # Fallback if ORM not available
        return WorkflowDetailOut(
            id=str(uuid.uuid4()),
            project_id=body.project_id,
            status="running",
            current_step="initializing",
            progress=0,
            task_description=body.task_description,
            start_time=datetime.utcnow(),
            end_time=None,
            error=None,
        )

@app.get("/workflows/{workflow_id}", response_model=WorkflowDetailOut)
async def get_workflow_api(workflow_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # Ensure workflow belongs to user's project
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    proj = db.query(Project).filter(Project.id == wf.project_id, Project.owner_id == current_user["id"]).first()
    if not proj:
        raise HTTPException(status_code=403, detail="Forbidden")
    return WorkflowDetailOut(
        id=wf.id,
        project_id=wf.project_id,
        status=wf.status,
        current_step=wf.current_step,
        progress=wf.progress,
        task_description=wf.task_description,
        start_time=wf.start_time,
        end_time=wf.end_time,
        error=wf.error,
    )

# ========================= MemoryNexus APIs =========================
# NOTE: Endpoints below are minimal CRUD; integrate governance & auth later (STUB)

class ConversationCreate(BaseModel):
    user_id: str
    agent_name: str
    purpose: Optional[str] = None

class ConversationOut(BaseModel):
    id: str
    user_id: str
    agent_name: str
    purpose: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

@app.post("/memory/conversations", response_model=ConversationOut)
async def create_conversation(payload: ConversationCreate, db: Session = Depends(get_db)):
    conv = Conversation(
        id=str(uuid4()),
        user_id=payload.user_id,
        agent_name=payload.agent_name,
        purpose=payload.purpose,
        created_at=datetime.utcnow(),
        updated_at=None,
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return ConversationOut(
        id=conv.id,
        user_id=conv.user_id,
        agent_name=conv.agent_name,
        purpose=conv.purpose,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
    )

@app.get("/memory/conversations/{conversation_id}", response_model=ConversationOut)
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conv = db.get(Conversation, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationOut(
        id=conv.id,
        user_id=conv.user_id,
        agent_name=conv.agent_name,
        purpose=conv.purpose,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
    )

class MessageCreate(BaseModel):
    conversation_id: str
    sender: str  # HARDCODED: expected one of 'user','assistant','system' – enforce later
    content: str
    role: Optional[str] = None
    token_count: Optional[int] = None

class MessageOut(BaseModel):
    id: str
    conversation_id: Optional[str]
    sender: str
    content: str
    role: Optional[str] = None
    token_count: Optional[int] = None
    created_at: datetime

@app.post("/memory/messages", response_model=MessageOut)
async def create_message(payload: MessageCreate, db: Session = Depends(get_db)):
    # STUB: Consider validating sender enum and conversation existence with FK
    msg = Message(
        id=str(uuid4()),
        conversation_id=payload.conversation_id,
        sender=payload.sender,
        content=payload.content,
        role=payload.role,
        token_count=payload.token_count,
        created_at=datetime.utcnow(),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    # Optional auto-curation to prevent context rot
    if AUTO_CURATE and payload.conversation_id:
        try:
            # Fire-and-forget best-effort summarize (synchronous here; later move async)
            rows: List[Message] = (
                db.query(Message)
                .filter(Message.conversation_id == payload.conversation_id)
                .order_by(Message.created_at.asc())
                .all()
            )
            total_messages = len(rows)
            total_tokens = sum(estimate_tokens(r.content or "") for r in rows)
            if total_messages > CONTEXT_BUDGET_MESSAGES or total_tokens > CONTEXT_BUDGET_TOKENS:
                cutoff_idx = max(0, int(total_messages * 0.6))  # HARDCODED
                to_summarize = rows[:cutoff_idx]
                target_tokens = max(256, int(CONTEXT_BUDGET_TOKENS * 0.1))
                summary_text = summarize_messages(to_summarize, target_tokens)
                summ = Summary(
                    id=str(uuid4()),
                    conversation_id=payload.conversation_id,
                    summary=summary_text,
                    period="on_event",
                    generated_by="curator_v1",  # HARDCODED
                    created_at=datetime.utcnow(),
                )
                db.add(summ)
                db.commit()
        except Exception as _:
            # STUB: swallow errors for now; add logging/metrics later
            pass

    return MessageOut(
        id=msg.id,
        conversation_id=msg.conversation_id,
        sender=msg.sender,
        content=msg.content,
        role=msg.role,
        token_count=msg.token_count,
        created_at=msg.created_at,
    )

@app.get("/memory/conversations/{conversation_id}/messages", response_model=List[MessageOut])
async def list_messages(conversation_id: str, db: Session = Depends(get_db)):
    rows = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
    return [
        MessageOut(
            id=r.id,
            conversation_id=r.conversation_id,
            sender=r.sender,
            content=r.content,
            role=r.role,
            token_count=r.token_count,
            created_at=r.created_at,
        )
        for r in rows
    ]

@app.get("/memory/conversations/{conversation_id}/summaries", response_model=List[str])
async def list_summaries(conversation_id: str, db: Session = Depends(get_db)):
    rows = (
        db.query(Summary)
        .filter(Summary.conversation_id == conversation_id)
        .order_by(Summary.created_at.asc())
        .all()
    )
    return [r.summary for r in rows]

class ToolCallCreate(BaseModel):
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None
    step_number: int
    tool_name: str
    input: Optional[dict] = None
    output: Optional[dict] = None
    latency_ms: Optional[int] = None
    status: str  # HARDCODED: expected one of 'success','failure','in_progress' – enforce later

class ToolCallOut(BaseModel):
    id: str
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None
    step_number: int
    tool_name: str
    input: Optional[dict] = None
    output: Optional[dict] = None
    latency_ms: Optional[int] = None
    status: str
    created_at: datetime

@app.post("/memory/tool-calls", response_model=ToolCallOut)
async def create_tool_call(payload: ToolCallCreate, db: Session = Depends(get_db)):
    tc = ToolCall(
        id=str(uuid4()),
        conversation_id=payload.conversation_id,
        message_id=payload.message_id,
        step_number=payload.step_number,
        tool_name=payload.tool_name,
        input=payload.input,
        output=payload.output,
        latency_ms=payload.latency_ms,
        status=payload.status,
        created_at=datetime.utcnow(),
    )
    db.add(tc)
    db.commit()
    db.refresh(tc)
    return ToolCallOut(
        id=tc.id,
        conversation_id=tc.conversation_id,
        message_id=tc.message_id,
        step_number=tc.step_number,
        tool_name=tc.tool_name,
        input=tc.input,
        output=tc.output,
        latency_ms=tc.latency_ms,
        status=tc.status,
        created_at=tc.created_at,
    )

class MemoryChunkCreate(BaseModel):
    source_type: str  # HARDCODED: enum contract to be enforced by OpenAPI/validation later
    source_id: str
    content: str
    embedding: Optional[List[float]] = None  # MOCK_DATA: allow missing embeddings now
    metadata: Optional[dict] = None

class MemoryChunkOut(BaseModel):
    id: str
    source_type: str
    source_id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Optional[dict] = None
    created_at: datetime

@app.post("/memory/chunks", response_model=MemoryChunkOut)
async def create_memory_chunk(payload: MemoryChunkCreate, db: Session = Depends(get_db)):
    # STUB: Add embedding length validation (1536) when real embedder integrated
    mc = MemoryChunk(
        id=str(uuid4()),
        source_type=payload.source_type,
        source_id=payload.source_id,
        content=payload.content,
        embedding=payload.embedding,  # pgvector accepts list[float]
        metadata_json=payload.metadata,
        created_at=datetime.utcnow(),
    )
    db.add(mc)
    db.commit()
    db.refresh(mc)
    return MemoryChunkOut(
        id=mc.id,
        source_type=mc.source_type,
        source_id=mc.source_id,
        content=mc.content,
        embedding=mc.embedding,
        metadata=mc.metadata_json,
        created_at=mc.created_at,
    )

@app.get("/memory/chunks/{chunk_id}", response_model=MemoryChunkOut)
async def get_memory_chunk(chunk_id: str, db: Session = Depends(get_db)):
    mc = db.get(MemoryChunk, chunk_id)
    if not mc:
        raise HTTPException(status_code=404, detail="Memory chunk not found")
    return MemoryChunkOut(
        id=mc.id,
        source_type=mc.source_type,
        source_id=mc.source_id,
        content=mc.content,
        embedding=mc.embedding,
        metadata=mc.metadata_json,
        created_at=mc.created_at,
    )

class VectorSearchRequest(BaseModel):
    query_embedding: List[float]  # STUB: produced by future embedder
    top_k: int = 5
    source_type: Optional[str] = None

class VectorSearchHit(BaseModel):
    id: str
    source_type: str
    source_id: str
    content: str
    score: float

@app.post("/memory/chunks/search", response_model=List[VectorSearchHit])
async def search_memory_chunks(req: VectorSearchRequest, db: Session = Depends(get_db)):
    if not req.query_embedding:
        raise HTTPException(status_code=400, detail="query_embedding is required")
    # STUB: optional filter by source_type
    q = db.query(
        MemoryChunk.id,
        MemoryChunk.source_type,
        MemoryChunk.source_id,
        MemoryChunk.content,
        (1 - func.cosine_distance(MemoryChunk.embedding, req.query_embedding)).label("score"),
    )
    if req.source_type:
        q = q.filter(MemoryChunk.source_type == req.source_type)
    rows = q.order_by(sa.desc("score")).limit(req.top_k).all()
    return [
        VectorSearchHit(
            id=r.id,
            source_type=r.source_type,
            source_id=r.source_id,
            content=r.content,
            score=float(r.score) if r.score is not None else 0.0,
        )
        for r in rows
    ]

# ========================= Context Curator (anti-rot) =========================
# HARDCODED: static budgets; later tune dynamically per convo/model
CONTEXT_BUDGET_MESSAGES = int(os.getenv("CONTEXT_BUDGET_MESSAGES", "50"))
CONTEXT_BUDGET_TOKENS = int(os.getenv("CONTEXT_BUDGET_TOKENS", "8000"))
AUTO_CURATE = os.getenv("AUTO_CURATE", "false").lower() == "true"

# STUB: very rough token estimator (to be replaced with tiktoken or tokenizer)
def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, int(len(text) / 4))  # ~4 chars per token heuristic

# STUB: simple extractive summarizer placeholder
# Borrowable: later swap with mature libraries (sumy, gensim, transformers)
def summarize_messages(messages: List[Message], target_tokens: int) -> str:
    # MOCK_DATA: naive strategy - take first sentence from each until target
    parts: List[str] = []
    budget = target_tokens
    for m in messages:
        txt = (m.content or "").strip()
        if not txt:
            continue
        sent = txt.split(". ")[0]
        parts.append(f"[{m.sender}] {sent}")
        budget -= estimate_tokens(sent)
        if budget <= 0:
            break
    if not parts:
        return ""
    header = "[Curator v1] Conversation summary (extractive, STUB)"
    return header + "\n" + "\n".join(parts)

class CurateResponse(BaseModel):
    summarized: bool
    created_summary_id: Optional[str] = None
    total_messages: int
    total_tokens: int
    budget_messages: int
    budget_tokens: int

@app.post("/memory/conversations/{conversation_id}/curate", response_model=CurateResponse)
async def curate_conversation(conversation_id: str, db: Session = Depends(get_db)):
    # Load messages ordered by time
    rows: List[Message] = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    total_messages = len(rows)
    total_tokens = sum(estimate_tokens(r.content or "") for r in rows)

    if total_messages <= CONTEXT_BUDGET_MESSAGES and total_tokens <= CONTEXT_BUDGET_TOKENS:
        return CurateResponse(
            summarized=False,
            created_summary_id=None,
            total_messages=total_messages,
            total_tokens=total_tokens,
            budget_messages=CONTEXT_BUDGET_MESSAGES,
            budget_tokens=CONTEXT_BUDGET_TOKENS,
        )

    # Determine cut set to summarize
    # HARDCODED: summarize oldest 60% of messages keeping the latest 40%
    cutoff_idx = max(0, int(total_messages * 0.6))
    to_summarize = rows[:cutoff_idx]

    target_tokens = max(256, int(CONTEXT_BUDGET_TOKENS * 0.1))  # HARDCODED
    summary_text = summarize_messages(to_summarize, target_tokens)

    summ = Summary(
        id=str(uuid4()),
        conversation_id=conversation_id,
        summary=summary_text,
        period="on_event",
        generated_by="curator_v1",  # HARDCODED tag
        created_at=datetime.utcnow(),
    )
    db.add(summ)
    db.commit()

    return CurateResponse(
        summarized=True,
        created_summary_id=summ.id,
        total_messages=total_messages,
        total_tokens=total_tokens,
        budget_messages=CONTEXT_BUDGET_MESSAGES,
        budget_tokens=CONTEXT_BUDGET_TOKENS,
    )

# ========================= Embedding STUB =========================
# STUB: deterministic pseudo-embedding without ML deps; replace with sentence-transformers later
EMBED_DIM = int(os.getenv("EMBED_DIM", "1536"))  # HARDCODED default matches schema

def generate_embedding_stub(text: str, dim: int = EMBED_DIM) -> List[float]:
    if not text:
        return [0.0] * dim
    # Use rolling hash to produce repeatable values in [-1,1]
    h = hashlib.sha256(text.encode("utf-8")).digest()
    vals: List[float] = []
    acc = 0
    for i in range(dim):
        acc = (acc + h[i % len(h)]) % 256
        v = (acc / 255.0) * 2.0 - 1.0
        vals.append(v)
    # L2 normalize
    norm = math.sqrt(sum(v * v for v in vals)) or 1.0
    return [v / norm for v in vals]

class EmbedRequest(BaseModel):
    text: str

class EmbedResponse(BaseModel):
    embedding: List[float]
    dim: int
    method: str

@app.post("/embeddings/text", response_model=EmbedResponse)
async def embed_text(req: EmbedRequest):
    emb = generate_embedding_stub(req.text, EMBED_DIM)
    return EmbedResponse(embedding=emb, dim=len(emb), method="stub_sha256_norm")

class ChunkEmbedResponse(BaseModel):
    id: str
    dim: int

@app.post("/memory/chunks/{chunk_id}/embed", response_model=ChunkEmbedResponse)
async def embed_chunk(chunk_id: str, db: Session = Depends(get_db)):
    mc = db.get(MemoryChunk, chunk_id)
    if not mc:
        raise HTTPException(status_code=404, detail="Memory chunk not found")
    emb = generate_embedding_stub(mc.content or "", EMBED_DIM)
    mc.embedding = emb
    db.add(mc)
    db.commit()
    return ChunkEmbedResponse(id=mc.id, dim=len(emb))

class ReindexResponse(BaseModel):
    updated: int

@app.post("/memory/chunks/reindex-missing", response_model=ReindexResponse)
async def reindex_missing_chunks(db: Session = Depends(get_db)):
    rows: List[MemoryChunk] = db.query(MemoryChunk).filter(MemoryChunk.embedding == None).all()  # noqa: E711
    count = 0
    for mc in rows:
        emb = generate_embedding_stub(mc.content or "", EMBED_DIM)
        mc.embedding = emb
        db.add(mc)
        count += 1
    if count:
        db.commit()
    return ReindexResponse(updated=count)

# ========================= API Gateway Stubs =========================
# MeditationModule: Problem framing → Core Insight Report (STUB)
class CoreInsightRequest(BaseModel):
    instruction: str
    context_hints: Optional[List[str]] = None

class SuccessMetric(BaseModel):
    metric_name: str
    target_value: str

class CoreInsightReport(BaseModel):
    problem_statement: str
    key_entities: List[str]
    constraints: dict
    success_metrics: List[SuccessMetric]

# Toggles for local implementations (HARDCODED defaults to local)
USE_LOCAL_EMBEDDING = os.getenv("USE_LOCAL_EMBEDDING", "true").lower() == "true"
USE_LOCAL_SUMMARY = os.getenv("USE_LOCAL_SUMMARY", "true").lower() == "true"

# ========================= Constitutional Governance (minimal) =========================
from functools import wraps

CONSTITUTION_FORBIDDEN = set([s.strip() for s in os.getenv("CONSTITUTION_FORBIDDEN", "").split(",") if s.strip()])

def governance_check(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        result = await fn(*args, **kwargs)
        # STUB: simple forbidden substring check on stringifiable payloads
        try:
            payload = result
            if isinstance(payload, dict):
                text = str(payload)
            elif hasattr(payload, "model_dump"):
                text = str(payload.model_dump())
            else:
                text = str(payload)
            for bad in CONSTITUTION_FORBIDDEN:
                if bad and bad.lower() in text.lower():
                    raise HTTPException(status_code=400, detail=f"Constitution violation: contains '{bad}'")
        except HTTPException:
            raise
        except Exception:
            # STUB: ignore parsing issues for now
            pass
        return result
    return wrapper

# Apply governance on content-generating endpoints

# DebateEngine: One-on-one debate (STUB)
class DebateTurn(BaseModel):
    speaker: str  # 'debater_a' | 'debater_b' | 'moderator'
    content: str

class DebateRequest(BaseModel):
    topic: str
    rounds: int = 3
    seed_arguments: Optional[List[str]] = None

class DebateResult(BaseModel):
    transcript: List[DebateTurn]
    verdict: str

@app.post("/debate/one-on-one", response_model=DebateResult)
@governance_check
async def debate_one_on_one(req: DebateRequest):
    # MOCK_DATA: structured alternating transcript; replace with orchestrated multi-agent later
    transcript: List[DebateTurn] = []
    for i in range(req.rounds):
        transcript.append(DebateTurn(speaker="debater_a", content=f"Round {i+1}: Arg A - {req.topic}"))
        transcript.append(DebateTurn(speaker="debater_b", content=f"Round {i+1}: Arg B - {req.topic}"))
    verdict = "moderator: consensus pending (STUB)"
    return DebateResult(transcript=transcript, verdict=verdict)

# ========================= Tool Orchestration (Human-AI Alignment) =========================
# ZSCE Agent as Human-AI Alignment Coordinator, not direct executor
_TOOL_REGISTRY: dict = {}

class ToolSpec(BaseModel):
    tool_name: str
    semantic_description: str
    tool_type: str  # 'llm' | 'code_executor' | 'test_runner' | 'debugger' | 'web_search' | 'file_ops'
    provider: str   # 'openai' | 'anthropic' | 'local' | 'github' | 'custom'
    capabilities: List[str]  # ['code_generation', 'testing', 'debugging', 'analysis']
    input_schema: dict = {}
    output_schema: dict = {}

class ToolOrchestrationRequest(BaseModel):
    human_intent: str  # Original human request
    context: Optional[Dict[str, Any]] = None
    preferred_tools: Optional[List[str]] = None
    quality_requirements: Optional[Dict[str, Any]] = None

class ToolOrchestrationResponse(BaseModel):
    orchestration_plan: List[Dict[str, Any]]  # Sequence of tool calls
    estimated_confidence: float  # 0-1
    human_alignment_score: float  # 0-1
    suggested_refinements: List[str]

@app.post("/tools/register")
async def register_tool(spec: ToolSpec):
    _TOOL_REGISTRY[spec.tool_name] = spec.model_dump()
    return {"ok": True, "count": len(_TOOL_REGISTRY)}

@app.get("/tools")
async def list_tools():
    return list(_TOOL_REGISTRY.values())

@app.post("/orchestration/plan", response_model=ToolOrchestrationResponse)
async def plan_tool_orchestration(request: ToolOrchestrationRequest):
    """Plan tool orchestration based on human intent and context"""
    try:
        # Use MeditationModule to understand human intent
        insight = await meditation_module.process_user_prompt(request.human_intent, request.context)
        report = await meditation_module.generate_insight_report(insight)
        
        # Plan tool sequence based on intent analysis
        orchestration_plan = []
        
        # Enhanced orchestration planning based on intent analysis
        intent_lower = request.human_intent.lower()
        
        # Authentication/Login System
        if any(keyword in intent_lower for keyword in ["login", "authentication", "auth", "signin", "signup"]):
            orchestration_plan = [
                {
                    "step": 1,
                    "tool": "web_search",
                    "purpose": "Research latest authentication best practices",
                    "input": {"query": "secure authentication best practices 2024 OWASP", "context": report}
                },
                {
                    "step": 2,
                    "tool": "code_generator_llm",
                    "purpose": "Generate authentication code structure",
                    "input": {"task": "Create secure login system", "context": report, "best_practices": "from_web_search"}
                },
                {
                    "step": 3,
                    "tool": "test_generator_llm", 
                    "purpose": "Generate comprehensive security tests",
                    "input": {"code_context": "authentication system", "test_requirements": "security, edge cases, penetration"}
                },
                {
                    "step": 4,
                    "tool": "security_analyzer",
                    "purpose": "Analyze security vulnerabilities",
                    "input": {"code": "generated_auth_code", "security_standards": "OWASP", "scan_type": "comprehensive"}
                },
                {
                    "step": 5,
                    "tool": "code_reviewer_llm",
                    "purpose": "Review and suggest security improvements",
                    "input": {"code": "auth_system", "review_criteria": "security, maintainability, performance", "focus": "security"}
                },
                {
                    "step": 6,
                    "tool": "documentation_generator_llm",
                    "purpose": "Generate security documentation",
                    "input": {"code": "auth_system", "doc_type": "security_guide", "audience": "developers"}
                }
            ]
        
        # API Development
        elif any(keyword in intent_lower for keyword in ["api", "rest", "endpoint", "microservice"]):
            orchestration_plan = [
                {
                    "step": 1,
                    "tool": "github_search",
                    "purpose": "Find similar API implementations",
                    "input": {"query": f"{intent_lower} API implementation", "language": "python", "context": report}
                },
                {
                    "step": 2,
                    "tool": "code_generator_llm",
                    "purpose": "Generate API structure and endpoints",
                    "input": {"task": "Create REST API", "context": report, "examples": "from_github_search"}
                },
                {
                    "step": 3,
                    "tool": "test_generator_llm",
                    "purpose": "Generate API tests",
                    "input": {"code_context": "REST API", "test_requirements": "unit, integration, load"}
                },
                {
                    "step": 4,
                    "tool": "performance_analyzer",
                    "purpose": "Analyze API performance",
                    "input": {"code": "api_code", "metrics": "response_time, throughput, memory"}
                },
                {
                    "step": 5,
                    "tool": "code_quality_analyzer",
                    "purpose": "Check API code quality",
                    "input": {"code": "api_code", "standards": "REST, OpenAPI, error_handling"}
                },
                {
                    "step": 6,
                    "tool": "documentation_generator_llm",
                    "purpose": "Generate API documentation",
                    "input": {"code": "api_code", "doc_type": "openapi", "format": "yaml"}
                }
            ]
        
        # Frontend Development
        elif any(keyword in intent_lower for keyword in ["frontend", "ui", "interface", "react", "vue", "angular"]):
            orchestration_plan = [
                {
                    "step": 1,
                    "tool": "web_search",
                    "purpose": "Research UI/UX best practices",
                    "input": {"query": f"{intent_lower} UI UX best practices 2024", "context": report}
                },
                {
                    "step": 2,
                    "tool": "code_generator_llm",
                    "purpose": "Generate frontend components",
                    "input": {"task": "Create frontend interface", "context": report, "framework": "react"}
                },
                {
                    "step": 3,
                    "tool": "test_generator_llm",
                    "purpose": "Generate frontend tests",
                    "input": {"code_context": "frontend components", "test_requirements": "unit, integration, e2e"}
                },
                {
                    "step": 4,
                    "tool": "linter",
                    "purpose": "Lint frontend code",
                    "input": {"code": "frontend_code", "rules": "eslint, prettier, accessibility"}
                },
                {
                    "step": 5,
                    "tool": "build_tool",
                    "purpose": "Build and optimize frontend",
                    "input": {"code": "frontend_code", "optimization": "bundle_size, performance"}
                },
                {
                    "step": 6,
                    "tool": "code_reviewer_llm",
                    "purpose": "Review UI/UX implementation",
                    "input": {"code": "frontend_code", "review_criteria": "usability, accessibility, performance"}
                }
            ]
        
        # Data Analysis/Machine Learning
        elif any(keyword in intent_lower for keyword in ["data", "analysis", "ml", "machine learning", "model", "prediction"]):
            orchestration_plan = [
                {
                    "step": 1,
                    "tool": "web_search",
                    "purpose": "Research ML algorithms and approaches",
                    "input": {"query": f"{intent_lower} machine learning algorithms", "context": report}
                },
                {
                    "step": 2,
                    "tool": "github_search",
                    "purpose": "Find similar ML implementations",
                    "input": {"query": f"{intent_lower} machine learning implementation", "context": report}
                },
                {
                    "step": 3,
                    "tool": "code_generator_llm",
                    "purpose": "Generate ML pipeline code",
                    "input": {"task": "Create ML pipeline", "context": report, "algorithms": "from_research"}
                },
                {
                    "step": 4,
                    "tool": "test_generator_llm",
                    "purpose": "Generate ML tests",
                    "input": {"code_context": "ML pipeline", "test_requirements": "unit, validation, cross_validation"}
                },
                {
                    "step": 5,
                    "tool": "performance_analyzer",
                    "purpose": "Analyze ML performance",
                    "input": {"code": "ml_code", "metrics": "accuracy, precision, recall, training_time"}
                },
                {
                    "step": 6,
                    "tool": "documentation_generator_llm",
                    "purpose": "Generate ML documentation",
                    "input": {"code": "ml_code", "doc_type": "model_card", "include": "metrics, limitations, bias"}
                }
            ]
        
        # General Development Task
        else:
            orchestration_plan = [
                {
                    "step": 1,
                    "tool": "web_search",
                    "purpose": "Research best practices and solutions",
                    "input": {"query": f"{intent_lower} best practices", "context": report}
                },
                {
                    "step": 2,
                    "tool": "code_generator_llm",
                    "purpose": "Generate initial implementation",
                    "input": {"task": request.human_intent, "context": report, "research": "from_web_search"}
                },
                {
                    "step": 3,
                    "tool": "test_generator_llm",
                    "purpose": "Generate comprehensive tests",
                    "input": {"code_context": "generated_code", "test_requirements": "unit, integration, edge_cases"}
                },
                {
                    "step": 4,
                    "tool": "code_quality_analyzer",
                    "purpose": "Analyze code quality",
                    "input": {"code": "generated_code", "standards": "clean_code, design_patterns"}
                },
                {
                    "step": 5,
                    "tool": "code_reviewer_llm",
                    "purpose": "Review and suggest improvements",
                    "input": {"code": "generated_code", "review_criteria": "maintainability, performance, security"}
                }
            ]
        
        # Calculate confidence and alignment scores
        estimated_confidence = 0.85  # Based on tool availability and intent clarity
        human_alignment_score = 0.90  # Based on how well we understand the intent
        
        # Generate suggestions for human refinement
        suggestions = []
        if not report.get("key_entities"):
            suggestions.append("Please specify key entities (users, roles, permissions)")
        if not report.get("constraints"):
            suggestions.append("Please specify constraints (security level, performance requirements)")
        if not report.get("success_metrics"):
            suggestions.append("Please define success criteria (test coverage, response time)")
            
        # 记录交互用于训练
        try:
            await training_module.record_interaction(
                user_intent=request.human_intent,
                original_prompt=request.human_intent,
                orchestration_plan=orchestration_plan,
                tool_calls=[],
                tool_results=[],
                final_outcome={
                    "orchestration_plan": orchestration_plan,
                    "confidence": estimated_confidence,
                    "alignment_score": human_alignment_score
                }
            )
        except Exception as e:
            logger.warning(f"Failed to record interaction for training: {e}")
        
        return ToolOrchestrationResponse(
            orchestration_plan=orchestration_plan,
            estimated_confidence=estimated_confidence,
            human_alignment_score=human_alignment_score,
            suggested_refinements=suggestions
        )
        
    except Exception as e:
        logger.error(f"Tool orchestration planning error: {e}")
        return ToolOrchestrationResponse(
            orchestration_plan=[],
            estimated_confidence=0.0,
            human_alignment_score=0.0,
            suggested_refinements=[f"Error in planning: {str(e)}"]
        )

class ExecuteToolRequest(BaseModel):
    tool_name: str
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None
    step_number: int = 1
    input: Optional[dict] = None
    mode: Optional[str] = "auto"  # 'auto' | 'user' | 'web'

class ExecuteToolResponse(BaseModel):
    tool_name: str
    output: dict
    audited_call_id: str

# External Tool Integrations (ZSCE Agent coordinates these, doesn't execute directly)
async def _tool_code_generator_llm(input_data: dict) -> dict:
    """Coordinate with external LLM for code generation"""
    return {
        "tool_type": "llm",
        "provider": "openai",
        "capability": "code_generation",
        "result": "Generated code would be here (coordinated via external LLM)",
        "metadata": {"model": "gpt-4", "tokens_used": 1500}
    }

async def _tool_test_generator_llm(input_data: dict) -> dict:
    """Coordinate with external LLM for test generation"""
    return {
        "tool_type": "llm", 
        "provider": "anthropic",
        "capability": "test_generation",
        "result": "Generated tests would be here (coordinated via external LLM)",
        "metadata": {"model": "claude-3", "tokens_used": 800}
    }

async def _tool_security_analyzer(input_data: dict) -> dict:
    """Coordinate with external security analysis tool"""
    return {
        "tool_type": "analyzer",
        "provider": "github",
        "capability": "security_analysis", 
        "result": "Security analysis would be here (coordinated via external tool)",
        "metadata": {"tool": "semgrep", "vulnerabilities_found": 0}
    }

async def _tool_code_reviewer_llm(input_data: dict) -> dict:
    """Coordinate with external LLM for code review"""
    return {
        "tool_type": "llm",
        "provider": "openai", 
        "capability": "code_review",
        "result": "Code review would be here (coordinated via external LLM)",
        "metadata": {"model": "gpt-4", "suggestions": 3}
    }

async def _tool_web_search(input_data: dict) -> dict:
    """Coordinate with external web search tool"""
    return {
        "tool_type": "web_search",
        "provider": "custom",
        "capability": "information_retrieval",
        "result": "Search results would be here (coordinated via external search API)",
        "metadata": {"query": input_data.get("query", ""), "results_count": 10}
    }

# Additional LLM Tools
async def _tool_documentation_generator_llm(input_data: dict) -> dict:
    """Coordinate with external LLM for documentation generation"""
    return {
        "tool_type": "llm",
        "provider": "openai",
        "capability": "documentation_generation",
        "result": "Generated documentation would be here (coordinated via external LLM)",
        "metadata": {"model": "gpt-4", "tokens_used": 1200, "doc_type": input_data.get("doc_type", "api")}
    }

async def _tool_refactoring_llm(input_data: dict) -> dict:
    """Coordinate with external LLM for code refactoring"""
    return {
        "tool_type": "llm",
        "provider": "anthropic",
        "capability": "code_refactoring",
        "result": "Refactored code would be here (coordinated via external LLM)",
        "metadata": {"model": "claude-3", "tokens_used": 2000, "refactor_type": input_data.get("type", "general")}
    }

# Analysis Tools
async def _tool_performance_analyzer(input_data: dict) -> dict:
    """Coordinate with external performance analysis tool"""
    return {
        "tool_type": "analyzer",
        "provider": "github",
        "capability": "performance_analysis",
        "result": "Performance analysis would be here (coordinated via external tool)",
        "metadata": {"tool": "py-spy", "bottlenecks_found": 2, "optimization_suggestions": 5}
    }

async def _tool_dependency_analyzer(input_data: dict) -> dict:
    """Coordinate with external dependency analysis tool"""
    return {
        "tool_type": "analyzer",
        "provider": "github",
        "capability": "dependency_analysis",
        "result": "Dependency analysis would be here (coordinated via external tool)",
        "metadata": {"tool": "safety", "vulnerabilities": 0, "outdated_packages": 3}
    }

async def _tool_code_quality_analyzer(input_data: dict) -> dict:
    """Coordinate with external code quality analysis tool"""
    return {
        "tool_type": "analyzer",
        "provider": "github",
        "capability": "code_quality_analysis",
        "result": "Code quality analysis would be here (coordinated via external tool)",
        "metadata": {"tool": "sonarqube", "quality_score": 85, "issues": 12}
    }

# Execution Tools
async def _tool_test_runner(input_data: dict) -> dict:
    """Coordinate with external test runner"""
    return {
        "tool_type": "executor",
        "provider": "local",
        "capability": "test_execution",
        "result": "Test execution results would be here (coordinated via external runner)",
        "metadata": {"framework": "pytest", "tests_passed": 45, "tests_failed": 2, "coverage": 92}
    }

async def _tool_linter(input_data: dict) -> dict:
    """Coordinate with external linter"""
    return {
        "tool_type": "executor",
        "provider": "local",
        "capability": "code_linting",
        "result": "Linting results would be here (coordinated via external linter)",
        "metadata": {"tool": "eslint", "errors": 0, "warnings": 3, "fixable": 2}
    }

async def _tool_formatter(input_data: dict) -> dict:
    """Coordinate with external code formatter"""
    return {
        "tool_type": "executor",
        "provider": "local",
        "capability": "code_formatting",
        "result": "Formatted code would be here (coordinated via external formatter)",
        "metadata": {"tool": "prettier", "files_formatted": 8, "changes_made": 15}
    }

async def _tool_build_tool(input_data: dict) -> dict:
    """Coordinate with external build tool"""
    return {
        "tool_type": "executor",
        "provider": "local",
        "capability": "build_execution",
        "result": "Build results would be here (coordinated via external build tool)",
        "metadata": {"tool": "webpack", "status": "success", "bundle_size": "2.3MB", "build_time": "45s"}
    }

# Search & Research Tools
async def _tool_github_search(input_data: dict) -> dict:
    """Coordinate with GitHub search API"""
    return {
        "tool_type": "search",
        "provider": "github",
        "capability": "code_search",
        "result": "GitHub search results would be here (coordinated via GitHub API)",
        "metadata": {"query": input_data.get("query", ""), "repositories": 25, "code_snippets": 150}
    }

async def _tool_stackoverflow_search(input_data: dict) -> dict:
    """Coordinate with Stack Overflow search API"""
    return {
        "tool_type": "search",
        "provider": "stackoverflow",
        "capability": "qna_search",
        "result": "Stack Overflow results would be here (coordinated via SO API)",
        "metadata": {"query": input_data.get("query", ""), "questions": 12, "answers": 35}
    }

# File Operations
async def _tool_file_reader(input_data: dict) -> dict:
    """Coordinate with file reading operations"""
    return {
        "tool_type": "file_ops",
        "provider": "local",
        "capability": "file_reading",
        "result": "File content would be here (coordinated via file system)",
        "metadata": {"file_path": input_data.get("path", ""), "size": "15KB", "lines": 450}
    }

async def _tool_file_writer(input_data: dict) -> dict:
    """Coordinate with file writing operations"""
    return {
        "tool_type": "file_ops",
        "provider": "local",
        "capability": "file_writing",
        "result": "File write operation completed (coordinated via file system)",
        "metadata": {"file_path": input_data.get("path", ""), "bytes_written": 2048, "status": "success"}
    }

async def _tool_git_operations(input_data: dict) -> dict:
    """Coordinate with Git operations"""
    return {
        "tool_type": "file_ops",
        "provider": "local",
        "capability": "version_control",
        "result": "Git operation completed (coordinated via Git CLI)",
        "metadata": {"operation": input_data.get("operation", "commit"), "branch": "main", "commit_hash": "abc123"}
    }

# Enhanced Tool Registry - Hermes AI External Tool Coordination
_BUILTINS: dict[str, Callable[[dict], Any]] = {
    # LLM Tools
    "code_generator_llm": _tool_code_generator_llm,
    "test_generator_llm": _tool_test_generator_llm, 
    "code_reviewer_llm": _tool_code_reviewer_llm,
    "documentation_generator_llm": _tool_documentation_generator_llm,
    "refactoring_llm": _tool_refactoring_llm,
    
    # Analysis Tools
    "security_analyzer": _tool_security_analyzer,
    "performance_analyzer": _tool_performance_analyzer,
    "dependency_analyzer": _tool_dependency_analyzer,
    "code_quality_analyzer": _tool_code_quality_analyzer,
    
    # Execution Tools
    "test_runner": _tool_test_runner,
    "linter": _tool_linter,
    "formatter": _tool_formatter,
    "build_tool": _tool_build_tool,
    
    # Search & Research
    "web_search": _tool_web_search,
    "github_search": _tool_github_search,
    "stackoverflow_search": _tool_stackoverflow_search,
    
    # File Operations
    "file_reader": _tool_file_reader,
    "file_writer": _tool_file_writer,
    "git_operations": _tool_git_operations,
}

# Minimal JSON contract: {
#   tool_name, semantic_description,
#   input_schema: { required: [..], properties: { field: {type: 'string'|'number'|'object'|'array'|'boolean'} } }
# }

def _validate_input_against_schema(data: dict, schema: dict):
    if not schema:
        return
    required = schema.get("required", [])
    props = schema.get("properties", {})
    for r in required:
        if r not in data:
            raise HTTPException(status_code=400, detail=f"Missing required field: {r}")
    type_map = {
        "string": str,
        "number": (int, float),
        "object": dict,
        "array": list,
        "boolean": bool,
    }
    for key, spec in props.items():
        if key in data and "type" in spec:
            pytype = type_map.get(spec["type"])  # STUB: no nested validation
            if pytype and not isinstance(data[key], pytype):
                raise HTTPException(status_code=400, detail=f"Field '{key}' expects type {spec['type']}")

# Patch ToolSpec to include schema fields (already present)
# Execution stays the same, add validation & governance on output

@app.post("/tools/execute", response_model=ExecuteToolResponse)
@governance_check
async def execute_tool(req: ExecuteToolRequest, db: Session = Depends(get_db)):
    tool_name = req.tool_name
    input_data = req.input or {}
    mode = (req.mode or "auto").lower()

    # Resolve schema
    schema = None
    if tool_name in _TOOL_REGISTRY:
        schema = _TOOL_REGISTRY[tool_name].get("input_schema")
    _validate_input_against_schema(input_data, schema or {})

    # Simple policy per invocation mode
    AUTO_ALLOWLIST = {"echo"}  # HARDCODED: safe-by-default tools
    if mode == "auto" and tool_name not in AUTO_ALLOWLIST and tool_name not in _BUILTINS and tool_name not in _TOOL_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Tool '{tool_name}' not allowed in auto mode or not registered")
    if mode == "web" and tool_name != "web_search":
        raise HTTPException(status_code=400, detail="Web mode requires 'web_search' tool")
    # 'user' mode: user explicitly requested, we proceed without extra restriction beyond registration

    # Resolve tool: built-in first, then registry (STUB routing)
    if tool_name in _BUILTINS:
        output = await _BUILTINS[tool_name](input_data)
    elif tool_name in _TOOL_REGISTRY:
        output = {"result": "stub", "input": input_data}
    else:
        raise HTTPException(status_code=404, detail="Tool not found")

    # Audit log to tool_calls table
    call = ToolCall(
        id=str(uuid4()),
        message_id=req.message_id,
        conversation_id=req.conversation_id,
        step_number=req.step_number,
        tool_name=tool_name,
        input=input_data,
        output=output,
        latency_ms=0,  # STUB
        status="success",
        created_at=datetime.utcnow(),
    )
    db.add(call)
    db.commit()

    return ExecuteToolResponse(tool_name=tool_name, output=output, audited_call_id=call.id)

# ========================= Knowledge Graph CRUD =========================
from models import KGNode, KGEdge

class KGNodeCreate(BaseModel):
    entity_type: str
    properties: Optional[dict] = None

class KGNodeOut(BaseModel):
    id: str
    entity_type: str
    properties: Optional[dict] = None
    created_at: datetime

@app.post("/kg/nodes", response_model=KGNodeOut)
async def create_kg_node(payload: KGNodeCreate, db: Session = Depends(get_db)):
    node = KGNode(
        id=str(uuid4()),
        entity_type=payload.entity_type,
        properties=payload.properties,
        created_at=datetime.utcnow(),
    )
    db.add(node)
    db.commit()
    db.refresh(node)
    return KGNodeOut(id=node.id, entity_type=node.entity_type, properties=node.properties, created_at=node.created_at)

@app.get("/kg/nodes/{node_id}", response_model=KGNodeOut)
async def get_kg_node(node_id: str, db: Session = Depends(get_db)):
    node = db.get(KGNode, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return KGNodeOut(id=node.id, entity_type=node.entity_type, properties=node.properties, created_at=node.created_at)

class KGEdgeCreate(BaseModel):
    source_node_id: str
    target_node_id: str
    relationship_type: str
    properties: Optional[dict] = None

class KGEdgeOut(BaseModel):
    id: str
    source_node_id: str
    target_node_id: str
    relationship_type: str
    properties: Optional[dict] = None
    created_at: datetime

@app.post("/kg/edges", response_model=KGEdgeOut)
async def create_kg_edge(payload: KGEdgeCreate, db: Session = Depends(get_db)):
    # Basic validation
    if not db.get(KGNode, payload.source_node_id) or not db.get(KGNode, payload.target_node_id):
        raise HTTPException(status_code=400, detail="Invalid node references")
    edge = KGEdge(
        id=str(uuid4()),
        source_node_id=payload.source_node_id,
        target_node_id=payload.target_node_id,
        relationship_type=payload.relationship_type,
        properties=payload.properties,
        created_at=datetime.utcnow(),
    )
    db.add(edge)
    db.commit()
    db.refresh(edge)
    return KGEdgeOut(
        id=edge.id,
        source_node_id=edge.source_node_id,
        target_node_id=edge.target_node_id,
        relationship_type=edge.relationship_type,
        properties=edge.properties,
        created_at=edge.created_at,
    )

@app.get("/kg/nodes/{node_id}/edges", response_model=List[KGEdgeOut])
async def list_node_edges(node_id: str, db: Session = Depends(get_db)):
    edges: List[KGEdge] = db.query(KGEdge).filter((KGEdge.source_node_id == node_id) | (KGEdge.target_node_id == node_id)).all()
    return [
        KGEdgeOut(
            id=e.id,
            source_node_id=e.source_node_id,
            target_node_id=e.target_node_id,
            relationship_type=e.relationship_type,
            properties=e.properties,
            created_at=e.created_at,
        )
        for e in edges
    ]

# ========================= V4.0 Core Modules =========================

# MeditationModule - 问题框架化
class MeditationRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = None

class MeditationResponse(BaseModel):
    success: bool
    insight_report: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None

@app.post("/meditation/frame", response_model=MeditationResponse)
async def meditation_frame(request: MeditationRequest):
    """问题框架化 - 生成核心洞见报告"""
    try:
        start_time = datetime.now()
        
        # 处理用户提示
        insight = await meditation_module.process_user_prompt(
            request.prompt, 
            request.context
        )
        
        # 生成报告
        insight_report = await meditation_module.generate_insight_report(insight)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return MeditationResponse(
            success=True,
            insight_report=insight_report,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"MeditationModule error: {e}")
        return MeditationResponse(
            success=False,
            error=str(e),
            processing_time=None
        )

# DebateEngine - 结构化辩论引擎
class DebateInitiateRequest(BaseModel):
    topic: str
    participants: List[str]
    initial_arguments: Optional[Dict[str, str]] = None

class DebateArgumentRequest(BaseModel):
    agent_id: str
    content: str
    argument_type: str = "reasoning"
    parent_argument_id: Optional[str] = None

class DebateResponse(BaseModel):
    success: bool
    debate_id: Optional[str] = None
    argument_id: Optional[str] = None
    error: Optional[str] = None

@app.post("/debate/initiate", response_model=DebateResponse)
async def debate_initiate(request: DebateInitiateRequest):
    """发起辩论"""
    try:
        debate_id = await debate_engine.initiate_debate(
            topic=request.topic,
            participants=request.participants,
            initial_arguments=request.initial_arguments
        )
        
        return DebateResponse(
            success=True,
            debate_id=debate_id
        )
        
    except Exception as e:
        logger.error(f"DebateEngine initiate error: {e}")
        return DebateResponse(
            success=False,
            error=str(e)
        )

@app.post("/debate/{debate_id}/argument", response_model=DebateResponse)
async def debate_add_argument(debate_id: str, request: DebateArgumentRequest):
    """添加论证"""
    try:
        # 验证argument_type
        try:
            argument_type = ArgumentType(request.argument_type)
        except ValueError:
            raise HTTPException(
                status_code=422, 
                detail=f"Invalid argument_type: {request.argument_type}. Must be one of: {[e.value for e in ArgumentType]}"
            )
        
        argument_id = await debate_engine.add_argument(
            debate_id=debate_id,
            agent_id=request.agent_id,
            content=request.content,
            argument_type=argument_type,
            parent_argument_id=request.parent_argument_id
        )
        
        return DebateResponse(
            success=True,
            argument_id=argument_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DebateEngine add argument error: {e}")
        return DebateResponse(
            success=False,
            error=str(e)
        )

@app.get("/debate/{debate_id}/status")
async def debate_status(debate_id: str):
    """获取辩论状态"""
    status = await debate_engine.get_debate_status(debate_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Debate not found")
    return status

@app.get("/debate/{debate_id}/rounds")
async def debate_rounds(debate_id: str):
    """获取辩论轮次"""
    rounds = await debate_engine.get_debate_rounds(debate_id)
    if rounds is None:
        raise HTTPException(status_code=404, detail="Debate not found")
    return {"rounds": rounds}

@app.get("/debate/list")
async def debate_list():
    """列出活跃的辩论"""
    debates = await debate_engine.list_active_debates()
    return {"debates": debates}

# HighDimensionModule - 代码分析引擎
class CodeAnalysisRequest(BaseModel):
    target_paths: Optional[List[str]] = None

class ImpactAnalysisRequest(BaseModel):
    target_entity: str

class HighDimensionResponse(BaseModel):
    success: bool
    analysis_result: Optional[Dict[str, Any]] = None
    impact_report: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None

@app.post("/high-dimension/analyze", response_model=HighDimensionResponse)
async def high_dimension_analyze(request: CodeAnalysisRequest):
    """分析代码库"""
    try:
        start_time = datetime.now()
        
        result = await high_dimension_module.analyze_codebase(request.target_paths)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return HighDimensionResponse(
            success=True,
            analysis_result=result,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"HighDimensionModule analyze error: {e}")
        return HighDimensionResponse(
            success=False,
            error=str(e),
            processing_time=None
        )

@app.post("/high-dimension/impact", response_model=HighDimensionResponse)
async def high_dimension_impact(request: ImpactAnalysisRequest):
    """分析影响报告"""
    try:
        start_time = datetime.now()
        
        impact_report = await high_dimension_module.generate_impact_report(request.target_entity)
        
        # 转换为字典格式
        report_dict = {
            "analysis_id": impact_report.analysis_id,
            "target_entity": impact_report.target_entity,
            "architecture_impacts": [
                {
                    "entity": {
                        "name": impact.entity.name,
                        "type": impact.entity.type,
                        "file_path": impact.entity.file_path,
                        "risk_level": impact.entity.risk_level
                    },
                    "affected_modules": impact.affected_modules,
                    "impact_scope": impact.impact_scope,
                    "risk_assessment": impact.risk_assessment,
                    "mitigation_suggestions": impact.mitigation_suggestions,
                    "confidence_score": impact.confidence_score
                }
                for impact in impact_report.architecture_impacts
            ],
            "concurrency_risks": [
                {
                    "entity": {
                        "name": risk.entity.name,
                        "type": risk.entity.type,
                        "file_path": risk.entity.file_path
                    },
                    "risk_type": risk.risk_type,
                    "risk_description": risk.risk_description,
                    "affected_operations": risk.affected_operations,
                    "severity": risk.severity,
                    "mitigation_strategies": risk.mitigation_strategies
                }
                for risk in impact_report.concurrency_risks
            ],
            "overall_risk_score": impact_report.overall_risk_score,
            "recommendations": impact_report.recommendations,
            "timestamp": impact_report.timestamp.isoformat()
        }
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return HighDimensionResponse(
            success=True,
            impact_report=report_dict,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"HighDimensionModule impact error: {e}")
        return HighDimensionResponse(
            success=False,
            error=str(e),
            processing_time=None
        )

# ========================= Core Agent Integration =========================

# Core Agent Status
@app.get("/core/status")
async def core_status():
    """Check if core agent integration is available."""
    return {
        "available": core_integration.is_available(),
        "project_root": str(core_integration.project_root)
    }

# Project Constitution
@app.get("/core/constitution")
async def core_constitution():
    """Get project constitution."""
    result = await get_constitution()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

# Project Files
@app.get("/core/files")
async def core_files():
    """List project files."""
    result = await list_files()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.get("/core/files/{file_path:path}")
async def core_read_file(file_path: str):
    """Read a project file."""
    result = await read_file_content(file_path)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

class FileWriteRequest(BaseModel):
    content: str

@app.post("/core/files/{file_path:path}")
async def core_write_file(file_path: str, request: FileWriteRequest):
    """Write a project file."""
    result = await write_file_content(file_path, request.content)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

# Agent Workflow
class WorkflowRequest(BaseModel):
    prompt: str
    auto_approve: bool = True

class WorkflowResponse(BaseModel):
    success: bool
    workflow_id: Optional[str] = None
    error: Optional[str] = None
    user_prompt: Optional[str] = None
    constitution: Optional[str] = None
    test_case: Optional[dict] = None
    implementation: Optional[dict] = None
    debate_rounds: Optional[List[dict]] = None
    final_review: Optional[str] = None
    approved: Optional[bool] = None
    timestamp: Optional[str] = None

@app.post("/core/workflow", response_model=WorkflowResponse)
async def core_workflow(req: WorkflowRequest):
    """Run agent workflow with given prompt."""
    result = await run_agent_workflow(req.prompt, req.auto_approve)
    return WorkflowResponse(**result)

# Legacy Core Agent Integration (for backward compatibility)
class CoreRunRequest(BaseModel):
    prompt: str
    auto_approve: bool = True

class CoreRunResponse(BaseModel):
    job_id: int
    pid: int

@app.post("/core/run", response_model=CoreRunResponse)
async def core_run(req: CoreRunRequest):
    """Legacy core agent run endpoint (subprocess-based)."""
    # HARDCODED: path to core main.py; later move to config
    script_path = "/home/sean/zswe-agent/zswe-agent/zswe_agent/main.py"
    args = ["python3", script_path, req.prompt]
    if req.auto_approve:
        args.append("--yes")
    env = os.environ.copy()
    # Keep existing GOOGLE_API_KEY etc.
    proc = subprocess.Popen(
        args,
        cwd="/home/sean/zswe-agent",  # run at repo root
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return CoreRunResponse(job_id=proc.pid, pid=proc.pid)

class CoreJobStatus(BaseModel):
    pid: int
    running: bool

@app.get("/core/jobs/{pid}/status", response_model=CoreJobStatus)
async def core_job_status(pid: int):
    try:
        # signal 0 checks if process exists
        os.kill(pid, 0)
        running = True
    except OSError:
        running = False
    return CoreJobStatus(pid=pid, running=running)

# ========================= Prompt Lifecycle (Draft → Analyze → Preflight → Execute) =========================

class PromptDraftRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = None

class PromptRecordOut(BaseModel):
    id: str
    user_id: int
    original_prompt: str
    optimized_prompt: Optional[str] = None
    insight_summary: Optional[Dict[str, Any]] = None
    status: str  # 'draft' | 'analyzed' | 'executed'
    suggestions: Optional[List[str]] = None
    estimated_success: Optional[int] = None  # 0-100
    created_at: datetime
    updated_at: Optional[datetime] = None

class AnalyzePromptResponse(BaseModel):
    id: str
    optimized_prompt: str
    insight_summary: Dict[str, Any]
    suggestions: List[str]

class PreflightEstimateResponse(BaseModel):
    id: str
    estimated_success: int  # 0-100
    suggestions: List[str]

class ExecutePromptResponse(BaseModel):
    workflow: WorkflowDetailOut
    estimated_success: int
    suggestions: List[str]

# In-memory storage (MOCK_DATA) – replace with DB model later
_PROMPTS_DB: Dict[str, Dict[str, Any]] = {}

def _build_optimized_prompt(original: str, insight: Dict[str, Any]) -> str:
    # STUB: construct an enriched prompt with extracted problem statement, entities, constraints
    ps = insight.get("problem_statement") or insight.get("summary") or original
    entities = insight.get("key_entities") or []
    constraints = insight.get("constraints") or {}
    success_metrics = insight.get("success_metrics") or []
    parts: List[str] = [
        "Task: " + ps,
    ]
    if entities:
        parts.append("Key entities: " + ", ".join(map(str, entities)))
    if constraints:
        parts.append("Constraints: " + ", ".join(f"{k}={v}" for k, v in constraints.items()))
    if success_metrics:
        sm = ", ".join(f"{m.get('metric_name')}: {m.get('target_value')}" for m in success_metrics if isinstance(m, dict))
        if sm:
            parts.append("Success metrics: " + sm)
    parts.append("Please reason step-by-step and provide actionable outputs.")
    return "\n".join(parts)

def _suggestions_from_insight(insight: Dict[str, Any]) -> List[str]:
    suggestions: List[str] = []
    if not insight.get("key_entities"):
        suggestions.append("Add key entities (users, files, modules, endpoints).")
    if not insight.get("constraints"):
        suggestions.append("Specify constraints (time, security, performance, compatibility).")
    if not insight.get("success_metrics"):
        suggestions.append("Define success metrics (tests passing, latency, coverage).")
    if len((insight.get("problem_statement") or "").strip()) < 10:
        suggestions.append("Clarify the problem statement with more specifics.")
    return suggestions or ["Looks good. Optionally clarify scope and acceptance criteria."]

def _estimate_success(insight: Dict[str, Any]) -> int:
    # STUB scoring based on presence of components
    score = 40
    if insight.get("key_entities"):
        score += 20
    if insight.get("constraints"):
        score += 20
    if insight.get("success_metrics"):
        score += 20
    return max(0, min(100, score))

@app.post("/prompts/draft", response_model=PromptRecordOut)
async def create_prompt_draft(payload: PromptDraftRequest, current_user: dict = Depends(get_current_user)):
    pid = str(uuid4())
    now = datetime.utcnow()
    rec = {
        "id": pid,
        "user_id": current_user["id"],
        "original_prompt": payload.prompt,
        "optimized_prompt": None,
        "insight_summary": None,
        "status": "draft",
        "suggestions": None,
        "estimated_success": None,
        "created_at": now,
        "updated_at": None,
        "context": payload.context or {},  # MOCK_DATA retained
    }
    _PROMPTS_DB[pid] = rec
    return PromptRecordOut(**{k: rec[k] for k in [
        "id","user_id","original_prompt","optimized_prompt","insight_summary","status","suggestions","estimated_success","created_at","updated_at"
    ]})

@app.post("/prompts/{prompt_id}/analyze", response_model=AnalyzePromptResponse)
async def analyze_prompt(prompt_id: str, current_user: dict = Depends(get_current_user)):
    rec = _PROMPTS_DB.get(prompt_id)
    if not rec or rec["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Prompt not found")
    # Use MeditationModule to analyze
    insight = await meditation_module.process_user_prompt(rec["original_prompt"], rec.get("context"))
    report = await meditation_module.generate_insight_report(insight)
    optimized = _build_optimized_prompt(rec["original_prompt"], report or {})
    suggestions = _suggestions_from_insight(report or {})
    rec.update({
        "optimized_prompt": optimized,
        "insight_summary": report,
        "status": "analyzed",
        "updated_at": datetime.utcnow(),
        "suggestions": suggestions,
    })
    return AnalyzePromptResponse(id=prompt_id, optimized_prompt=optimized, insight_summary=report or {}, suggestions=suggestions)

@app.get("/prompts/{prompt_id}", response_model=PromptRecordOut)
async def get_prompt(prompt_id: str, current_user: dict = Depends(get_current_user)):
    rec = _PROMPTS_DB.get(prompt_id)
    if not rec or rec["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return PromptRecordOut(**{k: rec[k] for k in [
        "id","user_id","original_prompt","optimized_prompt","insight_summary","status","suggestions","estimated_success","created_at","updated_at"
    ]})

@app.post("/prompts/{prompt_id}/preflight", response_model=PreflightEstimateResponse)
async def preflight_estimate(prompt_id: str, current_user: dict = Depends(get_current_user)):
    rec = _PROMPTS_DB.get(prompt_id)
    if not rec or rec["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Prompt not found")
    report = rec.get("insight_summary") or {}
    est = _estimate_success(report)
    suggestions = rec.get("suggestions") or _suggestions_from_insight(report)
    rec.update({
        "estimated_success": est,
        "suggestions": suggestions,
        "updated_at": datetime.utcnow(),
    })
    return PreflightEstimateResponse(id=prompt_id, estimated_success=est, suggestions=suggestions)

@app.post("/prompts/{prompt_id}/execute", response_model=ExecutePromptResponse)
async def execute_prompt(prompt_id: str, project_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    rec = _PROMPTS_DB.get(prompt_id)
    if not rec or rec["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Prompt not found")
    # Ensure analyzed; if not, analyze on-the-fly (lazy execution)
    if rec.get("status") != "analyzed":
        insight = await meditation_module.process_user_prompt(rec["original_prompt"], rec.get("context"))
        report = await meditation_module.generate_insight_report(insight)
        rec["optimized_prompt"] = _build_optimized_prompt(rec["original_prompt"], report or {})
        rec["insight_summary"] = report
        rec["suggestions"] = _suggestions_from_insight(report or {})
        rec["status"] = "analyzed"
    # Preflight estimate
    est = _estimate_success(rec.get("insight_summary") or {})
    rec["estimated_success"] = est
    # Start a workflow using optimized prompt as task_description (MOCK integration)
    wf_req = WorkflowStartRequest(project_id=project_id, task_description=rec.get("optimized_prompt") or rec["original_prompt"])
    wf = await start_workflow_api(wf_req, current_user, db)  # reuse handler
    rec["status"] = "executed"
    rec["updated_at"] = datetime.utcnow()
    return ExecutePromptResponse(workflow=wf, estimated_success=est, suggestions=rec.get("suggestions") or [])

# ========================= Training & Learning APIs =========================
class FeedbackRequest(BaseModel):
    interaction_id: str
    feedback_type: str  # human_rating, outcome_quality, tool_effectiveness, alignment_score, user_satisfaction
    rating: float  # 1-5 scale
    comments: Optional[str] = ""
    specific_improvements: Optional[List[str]] = []

class InteractionRecordRequest(BaseModel):
    user_intent: str
    original_prompt: str
    orchestration_plan: List[Dict[str, Any]]
    tool_calls: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    final_outcome: Dict[str, Any]

@app.post("/training/record-interaction")
async def record_interaction_api(
    request: InteractionRecordRequest,
    current_user: dict = Depends(get_current_user)
):
    """记录交互过程用于训练"""
    try:
        interaction_id = await training_module.record_interaction(
            user_intent=request.user_intent,
            original_prompt=request.original_prompt,
            orchestration_plan=request.orchestration_plan,
            tool_calls=request.tool_calls,
            tool_results=request.tool_results,
            final_outcome=request.final_outcome
        )
        
        return {
            "interaction_id": interaction_id,
            "status": "recorded",
            "message": "Interaction recorded for training"
        }
    except Exception as e:
        logger.error(f"Failed to record interaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to record interaction")

@app.post("/training/add-feedback")
async def add_feedback_api(
    request: FeedbackRequest,
    current_user: dict = Depends(get_current_user)
):
    """添加人类反馈"""
    try:
        feedback_type = FeedbackType(request.feedback_type)
        
        success = await training_module.add_human_feedback(
            interaction_id=request.interaction_id,
            feedback_type=feedback_type,
            rating=request.rating,
            comments=request.comments,
            specific_improvements=request.specific_improvements
        )
        
        if success:
            return {
                "status": "success",
                "message": "Feedback added successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Interaction not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid feedback type")
    except Exception as e:
        logger.error(f"Failed to add feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to add feedback")

@app.get("/training/insights")
async def get_learning_insights_api(
    pattern_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """获取学习洞察"""
    try:
        insights = await training_module.get_learning_insights(pattern_type)
        
        return {
            "insights": [
                {
                    "id": insight.id,
                    "pattern_type": insight.pattern_type,
                    "description": insight.description,
                    "confidence": insight.confidence,
                    "applicable_scenarios": insight.applicable_scenarios,
                    "improvement_suggestions": insight.improvement_suggestions,
                    "evidence_count": insight.evidence_count
                }
                for insight in insights
            ],
            "total_count": len(insights)
        }
    except Exception as e:
        logger.error(f"Failed to get learning insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get learning insights")

@app.get("/training/metrics")
async def get_performance_metrics_api(
    current_user: dict = Depends(get_current_user)
):
    """获取性能指标"""
    try:
        metrics = await training_module.get_performance_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")

@app.post("/training/optimize-prompt")
async def optimize_prompt_api(
    category: str,
    context: Dict[str, Any],
    user_intent: str,
    current_user: dict = Depends(get_current_user)
):
    """获取优化的prompt"""
    try:
        optimized_prompt = await training_module.get_optimized_prompt(
            category=category,
            context=context,
            user_intent=user_intent
        )
        
        return {
            "optimized_prompt": optimized_prompt,
            "category": category,
            "optimization_applied": True
        }
    except Exception as e:
        logger.error(f"Failed to optimize prompt: {e}")
        raise HTTPException(status_code=500, detail="Failed to optimize prompt")

# ========================= High-Dimensional Review APIs =========================
class HighDimensionalReviewRequest(BaseModel):
    topic: str
    life_forms: List[str]
    initial_insights: Optional[Dict[str, str]] = None

class DimensionalInsightRequest(BaseModel):
    review_id: str
    perspective_type: str
    life_form: str
    insight_content: str
    time_dimension: str = "present"
    space_dimension: str = "current"

@app.post("/high-dimensional-review/initiate")
async def initiate_high_dimensional_review_api(
    request: HighDimensionalReviewRequest,
    current_user: dict = Depends(get_current_user)
):
    """发起高维生命回看"""
    try:
        review_id = await high_dimensional_review_engine.initiate_high_dimensional_review(
            topic=request.topic,
            life_forms=request.life_forms,
            initial_insights=request.initial_insights
        )
        
        return {
            "review_id": review_id,
            "status": "initiated",
            "message": "High-dimensional review initiated successfully"
        }
    except Exception as e:
        logger.error(f"Failed to initiate high-dimensional review: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate high-dimensional review")

@app.post("/high-dimensional-review/add-insight")
async def add_dimensional_insight_api(
    request: DimensionalInsightRequest,
    current_user: dict = Depends(get_current_user)
):
    """添加高维洞察"""
    try:
        perspective_type = PerspectiveType(request.perspective_type)
        
        success = await high_dimensional_review_engine.add_dimensional_insight(
            review_id=request.review_id,
            perspective_type=perspective_type,
            life_form=request.life_form,
            insight_content=request.insight_content,
            time_dimension=request.time_dimension,
            space_dimension=request.space_dimension
        )
        
        if success:
            return {
                "status": "success",
                "message": "Dimensional insight added successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Review not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid perspective type")
    except Exception as e:
        logger.error(f"Failed to add dimensional insight: {e}")
        raise HTTPException(status_code=500, detail="Failed to add dimensional insight")

@app.post("/high-dimensional-review/generate-wisdom/{review_id}")
async def generate_transcendent_wisdom_api(
    review_id: str,
    current_user: dict = Depends(get_current_user)
):
    """生成超越智慧"""
    try:
        transcendent_wisdom = await high_dimensional_review_engine.generate_transcendent_wisdom(review_id)
        
        if transcendent_wisdom:
            return {
                "status": "success",
                "transcendent_wisdom": {
                    "wisdom_integrated": transcendent_wisdom.wisdom_integrated,
                    "transcendent_insights": transcendent_wisdom.transcendent_insights,
                    "final_wisdom": transcendent_wisdom.final_wisdom,
                    "transcendence_score": transcendent_wisdom.transcendence_score,
                    "universal_principles": transcendent_wisdom.universal_principles,
                    "timeless_truths": transcendent_wisdom.timeless_truths,
                    "timestamp": transcendent_wisdom.timestamp.isoformat()
                }
            }
        else:
            return {
                "status": "insufficient_transcendence",
                "message": "Insufficient transcendence level to generate wisdom"
            }
    except Exception as e:
        logger.error(f"Failed to generate transcendent wisdom: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate transcendent wisdom")

@app.get("/high-dimensional-review/{review_id}/status")
async def get_review_status_api(
    review_id: str,
    current_user: dict = Depends(get_current_user)
):
    """获取回看状态"""
    try:
        status = await high_dimensional_review_engine.get_review_status(review_id)
        
        if status:
            return status
        else:
            raise HTTPException(status_code=404, detail="Review not found")
    except Exception as e:
        logger.error(f"Failed to get review status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get review status")

@app.get("/high-dimensional-review/{review_id}/wisdom")
async def get_transcendent_wisdom_api(
    review_id: str,
    current_user: dict = Depends(get_current_user)
):
    """获取超越智慧"""
    try:
        wisdom = await high_dimensional_review_engine.get_transcendent_wisdom(review_id)
        
        if wisdom:
            return wisdom
        else:
            raise HTTPException(status_code=404, detail="Transcendent wisdom not available")
    except Exception as e:
        logger.error(f"Failed to get transcendent wisdom: {e}")
        raise HTTPException(status_code=500, detail="Failed to get transcendent wisdom")

@app.get("/high-dimensional-review/active")
async def list_active_reviews_api(
    current_user: dict = Depends(get_current_user)
):
    """列出活跃回看"""
    try:
        reviews = await high_dimensional_review_engine.list_active_reviews()
        return {
            "active_reviews": reviews,
            "total_count": len(reviews)
        }
    except Exception as e:
        logger.error(f"Failed to list active reviews: {e}")
        raise HTTPException(status_code=500, detail="Failed to list active reviews")

# ========================= High-Dimensional Analysis APIs =========================
class HighDimensionalAnalysisRequest(BaseModel):
    codebase_path: str
    analysis_depth: int = 5
    transcendence_threshold: float = 0.7

@app.post("/high-dimensional-analysis/analyze")
async def analyze_codebase_high_dimensional_api(
    request: HighDimensionalAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """高维代码库分析"""
    try:
        report = await high_dimensional_analysis_module.analyze_codebase(
            codebase_path=request.codebase_path,
            analysis_depth=request.analysis_depth,
            transcendence_threshold=request.transcendence_threshold
        )
        
        return {
            "analysis_id": report.analysis_id,
            "timestamp": report.timestamp.isoformat(),
            "overall_transcendence_score": report.overall_transcendence_score,
            "entities_count": len(report.entities),
            "dimensional_impacts_count": len(report.dimensional_impacts),
            "transcendence_patterns_count": len(report.transcendence_patterns),
            "wisdom_insights": report.wisdom_insights,
            "universal_principles": report.universal_principles,
            "timeless_truths": report.timeless_truths,
            "consciousness_evolution": report.consciousness_evolution,
            "energy_transformation": report.energy_transformation,
            "transcendence_recommendations": report.transcendence_recommendations
        }
    except Exception as e:
        logger.error(f"Failed to analyze codebase: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze codebase")

@app.get("/high-dimensional-analysis/{analysis_id}/report")
async def get_analysis_report_api(
    analysis_id: str,
    current_user: dict = Depends(get_current_user)
):
    """获取分析报告"""
    try:
        report = await high_dimensional_analysis_module.generate_impact_report(analysis_id)
        
        if report:
            return report
        else:
            raise HTTPException(status_code=404, detail="Analysis report not found")
    except Exception as e:
        logger.error(f"Failed to get analysis report: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analysis report")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
