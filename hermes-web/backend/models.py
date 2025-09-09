"""
Database models for ZSCE Agent Web Application
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    bio = Column(Text)
    company = Column(String(100))
    location = Column(String(100))
    website = Column(String(200))
    is_active = Column(Boolean, default=True)
    role = Column(String(20), default="user")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    projects = relationship("Project", back_populates="owner")
    workflows = relationship("Workflow", back_populates="creator")
    notifications = relationship("Notification", back_populates="user")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    visibility = Column(String(20), default="private")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    members = relationship("ProjectMember", back_populates="project")
    workflows = relationship("Workflow", back_populates="project")
    files = relationship("ProjectFile", back_populates="project")

class ProjectMember(Base):
    __tablename__ = "project_members"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), default="member")
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User")

class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(String(50), primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    status = Column(String(20), default="pending")
    current_step = Column(String(200))
    progress = Column(Integer, default=0)
    task_description = Column(Text)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    error = Column(Text)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    debate_rounds = Column(Integer, default=0)
    estimated_completion = Column(DateTime)
    performance_metrics = Column(JSON)
    
    # Relationships
    project = relationship("Project", back_populates="workflows")
    creator = relationship("User", back_populates="workflows")
    code_changes = relationship("CodeChange", back_populates="workflow")
    debate_history = relationship("DebateRecord", back_populates="workflow")
    logs = relationship("WorkflowLog", back_populates="workflow")

class CodeChange(Base):
    __tablename__ = "code_changes"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String(50), ForeignKey("workflows.id"), nullable=False)
    file = Column(String(200), nullable=False)
    change_type = Column(String(20), nullable=False)  # added, modified, deleted
    lines_added = Column(Integer, default=0)
    lines_deleted = Column(Integer, default=0)
    summary = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="code_changes")

class DebateRecord(Base):
    __tablename__ = "debate_records"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String(50), ForeignKey("workflows.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    developer_message = Column(Text, nullable=False)
    reviewer_feedback = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # pending, accepted, rejected
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="debate_history")

class WorkflowLog(Base):
    __tablename__ = "workflow_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String(50), ForeignKey("workflows.id"), nullable=False)
    level = Column(String(20), nullable=False)  # info, warning, error, debug
    message = Column(Text, nullable=False)
    agent = Column(String(20))  # developer, reviewer, system
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="logs")

class ProjectFile(Base):
    __tablename__ = "project_files"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(200), nullable=False)
    file_type = Column(String(20), nullable=False)  # code, document, config
    size = Column(String(20))
    content_hash = Column(String(64))  # SHA-256 hash
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="files")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(20), nullable=False)  # workflow, project, team, system, security
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    is_read = Column(Boolean, default=False)
    action_url = Column(String(500))
    metadata_json = Column("metadata", JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notifications")

class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    theme = Column(String(20), default="auto")  # light, dark, auto
    language = Column(String(10), default="en-US")
    timezone = Column(String(50), default="UTC")
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    workflow_updates = Column(Boolean, default=True)
    project_changes = Column(Boolean, default=True)
    team_activities = Column(Boolean, default=True)
    system_alerts = Column(Boolean, default=False)
    security_notifications = Column(Boolean, default=True)
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5), default="22:00")
    quiet_hours_end = Column(String(5), default="08:00")
    
    # Relationships
    user = relationship("User")

class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    key_hash = Column(String(255), nullable=False)  # Hashed API key
    permissions = Column(JSON, default=list)
    last_used = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User")

class LoginHistory(Base):
    __tablename__ = "login_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ip_address = Column(String(45), nullable=False)  # IPv6 support
    user_agent = Column(Text)
    location = Column(String(100))
    success = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), nullable=False)
    agent_name = Column(String(100), nullable=False)
    purpose = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, index=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"))
    sender = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    role = Column(String(50))
    token_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class ToolCall(Base):
    __tablename__ = "tool_calls"
    
    id = Column(String(36), primary_key=True, index=True)
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="CASCADE"))
    conversation_id = Column(String(36), ForeignKey("conversations.id"))
    step_number = Column(Integer, nullable=False)
    tool_name = Column(String(100), nullable=False)
    input = Column(JSONB)
    output = Column(JSONB)
    latency_ms = Column(Integer)
    status = Column(String(20), nullable=False)  # 'success','failure','in_progress'
    created_at = Column(DateTime, default=datetime.utcnow)

class MemoryChunk(Base):
    __tablename__ = "memory_chunks"
    
    id = Column(String(36), primary_key=True, index=True)
    source_type = Column(String(50), nullable=False)  # 'message','document','code'
    source_id = Column(String(36), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))
    metadata_json = Column("metadata", JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

class Summary(Base):
    __tablename__ = "summaries"
    
    id = Column(String(36), primary_key=True, index=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"))
    summary = Column(Text, nullable=False)
    period = Column(String(20))  # 'hourly','daily','on_event'
    generated_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class KGNode(Base):
    __tablename__ = "kg_nodes"
    
    id = Column(String(36), primary_key=True, index=True)
    entity_type = Column(String(100), nullable=False)
    properties = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

class KGEdge(Base):
    __tablename__ = "kg_edges"
    
    id = Column(String(36), primary_key=True, index=True)
    source_node_id = Column(String(36), ForeignKey("kg_nodes.id", ondelete="CASCADE"))
    target_node_id = Column(String(36), ForeignKey("kg_nodes.id", ondelete="CASCADE"))
    relationship_type = Column(String(100), nullable=False)
    properties = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
