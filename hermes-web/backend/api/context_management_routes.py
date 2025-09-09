"""
Context Management API Routes
上下文管理API路由
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime

from services.context_management_service import (
    context_management_service,
    ContextType,
    ContextPriority
)

router = APIRouter(prefix="/context", tags=["context-management"])

class StoreContextRequest(BaseModel):
    """存储上下文请求"""
    content: str
    context_type: str
    priority: str = "medium"
    metadata: Optional[Dict[str, Any]] = None

class RetrieveContextRequest(BaseModel):
    """检索上下文请求"""
    query: str
    context_type: Optional[str] = None
    limit: int = 10

class SummarizeContextsRequest(BaseModel):
    """总结上下文请求"""
    context_ids: List[str]
    summary_type: str = "general"

class ContextResponse(BaseModel):
    """上下文响应"""
    id: str
    content: str
    context_type: str
    priority: str
    created_at: datetime
    last_accessed: datetime
    access_count: int
    importance_score: float
    compressed: bool
    summary: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SummaryResponse(BaseModel):
    """总结响应"""
    id: str
    summary_text: str
    key_points: List[str]
    entities: List[str]
    relationships: List[Dict[str, str]]
    quality_score: float

@router.post("/store", response_model=Dict[str, str])
async def store_context(request: StoreContextRequest):
    """存储上下文"""
    try:
        # 转换字符串为枚举
        context_type = ContextType(request.context_type)
        priority = ContextPriority(request.priority)
        
        context_id = await context_management_service.store_context(
            content=request.content,
            context_type=context_type,
            priority=priority,
            metadata=request.metadata
        )
        
        return {"context_id": context_id, "status": "success"}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid context type or priority: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store context: {str(e)}")

@router.post("/retrieve", response_model=List[ContextResponse])
async def retrieve_context(request: RetrieveContextRequest):
    """检索相关上下文"""
    try:
        context_type = None
        if request.context_type:
            context_type = ContextType(request.context_type)
        
        chunks = await context_management_service.retrieve_context(
            query=request.query,
            context_type=context_type,
            limit=request.limit
        )
        
        # 转换为响应格式
        responses = []
        for chunk in chunks:
            response = ContextResponse(
                id=chunk.id,
                content=chunk.content,
                context_type=chunk.context_type.value,
                priority=chunk.priority.value,
                created_at=chunk.created_at,
                last_accessed=chunk.last_accessed,
                access_count=chunk.access_count,
                importance_score=chunk.importance_score,
                compressed=chunk.compressed,
                summary=chunk.summary,
                metadata=chunk.metadata
            )
            responses.append(response)
        
        return responses
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid context type: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve context: {str(e)}")

@router.post("/compress/{context_id}", response_model=Dict[str, str])
async def compress_context(context_id: str):
    """压缩上下文"""
    try:
        success = await context_management_service.compress_context(context_id)
        
        if success:
            return {"status": "success", "message": "Context compressed successfully"}
        else:
            return {"status": "failed", "message": "Context not found or already compressed"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compress context: {str(e)}")

@router.post("/summarize", response_model=SummaryResponse)
async def summarize_contexts(request: SummarizeContextsRequest):
    """总结多个上下文"""
    try:
        summary_id = await context_management_service.summarize_contexts(
            context_ids=request.context_ids,
            summary_type=request.summary_type
        )
        
        # 获取总结详情
        summary = context_management_service.context_summaries.get(summary_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Summary not found")
        
        response = SummaryResponse(
            id=summary.id,
            summary_text=summary.summary_text,
            key_points=summary.key_points,
            entities=summary.entities,
            relationships=summary.relationships,
            quality_score=summary.quality_score
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to summarize contexts: {str(e)}")

@router.post("/prevent-decay", response_model=Dict[str, Any])
async def prevent_decay():
    """防止上下文腐烂"""
    try:
        decayed_count = await context_management_service.prevent_decay()
        
        return {
            "status": "success",
            "decayed_count": decayed_count,
            "message": f"Processed {decayed_count} decayed contexts"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to prevent decay: {str(e)}")

@router.get("/statistics", response_model=Dict[str, Any])
async def get_context_statistics():
    """获取上下文统计信息"""
    try:
        statistics = await context_management_service.get_context_statistics()
        return statistics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@router.get("/types", response_model=List[str])
async def get_context_types():
    """获取可用的上下文类型"""
    return [context_type.value for context_type in ContextType]

@router.get("/priorities", response_model=List[str])
async def get_context_priorities():
    """获取可用的上下文优先级"""
    return [priority.value for priority in ContextPriority]

@router.get("/summary/{summary_id}", response_model=SummaryResponse)
async def get_summary(summary_id: str):
    """获取总结详情"""
    try:
        summary = context_management_service.context_summaries.get(summary_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Summary not found")
        
        response = SummaryResponse(
            id=summary.id,
            summary_text=summary.summary_text,
            key_points=summary.key_points,
            entities=summary.entities,
            relationships=summary.relationships,
            quality_score=summary.quality_score
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

@router.delete("/context/{context_id}", response_model=Dict[str, str])
async def delete_context(context_id: str):
    """删除上下文"""
    try:
        if context_id in context_management_service.context_chunks:
            del context_management_service.context_chunks[context_id]
            return {"status": "success", "message": "Context deleted successfully"}
        else:
            return {"status": "failed", "message": "Context not found"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete context: {str(e)}")

@router.get("/health", response_model=Dict[str, str])
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "context-management"}
