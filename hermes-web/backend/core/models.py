"""
Core Data Models
松耦合的数据模型定义
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# 用户相关模型
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

# 项目相关模型
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

# 工作流相关模型
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

# 工具协调相关模型
class ToolSpec(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    provider: str
    capability: str

class ToolOrchestrationRequest(BaseModel):
    human_intent: str
    context: Optional[Dict[str, Any]] = None

class ToolOrchestrationResponse(BaseModel):
    orchestration_plan: List[Dict[str, Any]]
    estimated_confidence: float
    human_alignment_score: float
    suggested_refinements: List[str]

class ToolExecuteRequest(BaseModel):
    tool_name: str
    input_data: Dict[str, Any]
    mode: str = "auto"  # auto, user, web

class ToolExecuteResponse(BaseModel):
    tool_name: str
    output: Dict[str, Any]
    audited_call_id: str

# 训练相关模型
class FeedbackRequest(BaseModel):
    interaction_id: str
    feedback_type: str
    rating: float
    comments: Optional[str] = ""
    specific_improvements: Optional[List[str]] = []

class InteractionRecordRequest(BaseModel):
    user_intent: str
    original_prompt: str
    orchestration_plan: List[Dict[str, Any]]
    tool_calls: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    final_outcome: Dict[str, Any]

# 高维分析相关模型
class HighDimensionalAnalysisRequest(BaseModel):
    codebase_path: str
    analysis_depth: int = 5
    transcendence_threshold: float = 0.7

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

# 禅定模块相关模型
class MeditationRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = None

class MeditationResponse(BaseModel):
    success: bool
    insight_report: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None

# 辩论引擎相关模型
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
