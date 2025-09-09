"""
Prompt Optimizer API Routes
Prompt优化器API路由
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
from pydantic import BaseModel

from services.prompt_optimizer import prompt_optimizer

router = APIRouter(prefix="/prompt-optimizer", tags=["prompt-optimizer"])

class OptimizeRequest(BaseModel):
    user_command: str
    context: Dict[str, Any] = {}

@router.post("/optimize")
async def optimize_prompt(request: OptimizeRequest):
    """优化用户命令为精准prompt"""
    try:
        optimized_prompt = await prompt_optimizer.optimize_prompt(
            request.user_command, 
            request.context
        )
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "id": optimized_prompt.id,
                "original": optimized_prompt.original_command,
                "optimized": optimized_prompt.optimized_prompt,
                "context": optimized_prompt.context,
                "technical_requirements": optimized_prompt.technical_requirements,
                "user_stories": optimized_prompt.user_stories,
                "acceptance_criteria": optimized_prompt.acceptance_criteria,
                "quality_score": optimized_prompt.quality_score,
                "debate_rounds": optimized_prompt.debate_rounds,
                "constitution_checks": optimized_prompt.constitution_checks,
                "tool_recommendations": optimized_prompt.tool_recommendations,
                "created_at": optimized_prompt.created_at
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prompt optimization failed: {str(e)}")

@router.get("/constitution")
async def get_constitution():
    """获取宪法规则"""
    try:
        return JSONResponse(content={
            "success": True,
            "data": prompt_optimizer.constitution_rules
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get constitution: {str(e)}")

@router.get("/tools")
async def get_tool_catalog():
    """获取工具目录"""
    try:
        return JSONResponse(content={
            "success": True,
            "data": prompt_optimizer.tool_catalog
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tool catalog: {str(e)}")

@router.post("/validate")
async def validate_prompt(request: OptimizeRequest):
    """验证prompt质量"""
    try:
        # 这里可以添加更复杂的验证逻辑
        quality_indicators = {
            "has_technical_requirements": len(request.user_command) > 50,
            "has_user_context": "用户" in request.user_command or "user" in request.user_command.lower(),
            "has_functional_requirements": any(word in request.user_command.lower() for word in ["功能", "function", "需要", "need"]),
            "is_specific": len(request.user_command.split()) > 10
        }
        
        overall_score = sum(quality_indicators.values()) / len(quality_indicators)
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "quality_score": overall_score,
                "indicators": quality_indicators,
                "recommendations": [
                    "添加更多技术细节" if not quality_indicators["has_technical_requirements"] else None,
                    "明确用户角色和需求" if not quality_indicators["has_user_context"] else None,
                    "详细描述功能需求" if not quality_indicators["has_functional_requirements"] else None,
                    "提供更具体的描述" if not quality_indicators["is_specific"] else None
                ]
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prompt validation failed: {str(e)}")

Prompt Optimizer API Routes
Prompt优化器API路由
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
from pydantic import BaseModel

from services.prompt_optimizer import prompt_optimizer

router = APIRouter(prefix="/prompt-optimizer", tags=["prompt-optimizer"])

class OptimizeRequest(BaseModel):
    user_command: str
    context: Dict[str, Any] = {}

@router.post("/optimize")
async def optimize_prompt(request: OptimizeRequest):
    """优化用户命令为精准prompt"""
    try:
        optimized_prompt = await prompt_optimizer.optimize_prompt(
            request.user_command, 
            request.context
        )
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "id": optimized_prompt.id,
                "original": optimized_prompt.original_command,
                "optimized": optimized_prompt.optimized_prompt,
                "context": optimized_prompt.context,
                "technical_requirements": optimized_prompt.technical_requirements,
                "user_stories": optimized_prompt.user_stories,
                "acceptance_criteria": optimized_prompt.acceptance_criteria,
                "quality_score": optimized_prompt.quality_score,
                "debate_rounds": optimized_prompt.debate_rounds,
                "constitution_checks": optimized_prompt.constitution_checks,
                "tool_recommendations": optimized_prompt.tool_recommendations,
                "created_at": optimized_prompt.created_at
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prompt optimization failed: {str(e)}")

@router.get("/constitution")
async def get_constitution():
    """获取宪法规则"""
    try:
        return JSONResponse(content={
            "success": True,
            "data": prompt_optimizer.constitution_rules
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get constitution: {str(e)}")

@router.get("/tools")
async def get_tool_catalog():
    """获取工具目录"""
    try:
        return JSONResponse(content={
            "success": True,
            "data": prompt_optimizer.tool_catalog
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tool catalog: {str(e)}")

@router.post("/validate")
async def validate_prompt(request: OptimizeRequest):
    """验证prompt质量"""
    try:
        # 这里可以添加更复杂的验证逻辑
        quality_indicators = {
            "has_technical_requirements": len(request.user_command) > 50,
            "has_user_context": "用户" in request.user_command or "user" in request.user_command.lower(),
            "has_functional_requirements": any(word in request.user_command.lower() for word in ["功能", "function", "需要", "need"]),
            "is_specific": len(request.user_command.split()) > 10
        }
        
        overall_score = sum(quality_indicators.values()) / len(quality_indicators)
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "quality_score": overall_score,
                "indicators": quality_indicators,
                "recommendations": [
                    "添加更多技术细节" if not quality_indicators["has_technical_requirements"] else None,
                    "明确用户角色和需求" if not quality_indicators["has_user_context"] else None,
                    "详细描述功能需求" if not quality_indicators["has_functional_requirements"] else None,
                    "提供更具体的描述" if not quality_indicators["is_specific"] else None
                ]
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prompt validation failed: {str(e)}")
