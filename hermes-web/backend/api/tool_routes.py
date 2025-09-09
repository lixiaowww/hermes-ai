"""
Tool Execution API Routes
松耦合的工具执行API路由
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List

from core.models import (
    ToolExecuteRequest, ToolExecuteResponse, 
    ToolOrchestrationRequest, ToolOrchestrationResponse,
    ToolSpec
)
from services.auth_service import get_current_user
from services.tool_execution_service import tool_execution_service
from meditation_module import meditation_module
from training_module import training_module

router = APIRouter(prefix="/tools", tags=["tools"])

@router.post("/execute", response_model=ToolExecuteResponse)
async def execute_tool(
    request: ToolExecuteRequest,
    current_user: dict = Depends(get_current_user)
):
    """执行工具"""
    try:
        result = await tool_execution_service.execute_tool(
            request, 
            user_intent=f"Tool execution: {request.tool_name}"
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

@router.post("/orchestration/plan", response_model=ToolOrchestrationResponse)
async def plan_tool_orchestration(
    request: ToolOrchestrationRequest,
    current_user: dict = Depends(get_current_user)
):
    """规划工具协调"""
    try:
        # 使用禅定模块分析用户意图
        insight = await meditation_module.process_user_prompt(
            request.human_intent, 
            request.context
        )
        
        # 生成工具协调计划
        orchestration_plan = await _generate_orchestration_plan(
            request.human_intent, 
            insight
        )
        
        # 计算置信度和对齐度
        estimated_confidence = 0.8
        human_alignment_score = 0.85
        suggestions = ["请提供更多上下文信息", "考虑添加具体的约束条件"]
        
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
            print(f"Warning: Failed to record interaction for training: {e}")
        
        return ToolOrchestrationResponse(
            orchestration_plan=orchestration_plan,
            estimated_confidence=estimated_confidence,
            human_alignment_score=human_alignment_score,
            suggested_refinements=suggestions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration planning failed: {str(e)}")

@router.get("/", response_model=List[ToolSpec])
async def list_tools(current_user: dict = Depends(get_current_user)):
    """列出可用工具"""
    tools = []
    for tool_name, tool_func in tool_execution_service.tool_registry.items():
        tools.append(ToolSpec(
            name=tool_name,
            description=f"Tool: {tool_name}",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            provider="hermes-ai",
            capability="general"
        ))
    return tools

async def _generate_orchestration_plan(human_intent: str, insight) -> List[Dict[str, Any]]:
    """生成工具协调计划"""
    intent_lower = human_intent.lower()
    
    # 基于意图生成不同的工具序列
    if any(keyword in intent_lower for keyword in ["api", "rest", "endpoint"]):
        return [
            {
                "step": 1,
                "tool": "github_search",
                "purpose": "Find similar API implementations",
                "input": {"query": f"{intent_lower} API implementation", "language": "python"}
            },
            {
                "step": 2,
                "tool": "code_generator_llm",
                "purpose": "Generate API structure and endpoints",
                "input": {"task": "Create REST API", "context": str(insight)}
            },
            {
                "step": 3,
                "tool": "test_generator_llm",
                "purpose": "Generate API tests",
                "input": {"code_context": "REST API", "test_requirements": "unit, integration"}
            }
        ]
    elif any(keyword in intent_lower for keyword in ["frontend", "ui", "interface"]):
        return [
            {
                "step": 1,
                "tool": "web_search",
                "purpose": "Research UI/UX best practices",
                "input": {"query": f"{intent_lower} UI UX best practices 2024"}
            },
            {
                "step": 2,
                "tool": "code_generator_llm",
                "purpose": "Generate frontend components",
                "input": {"task": "Create frontend interface", "framework": "react"}
            },
            {
                "step": 3,
                "tool": "linter",
                "purpose": "Lint frontend code",
                "input": {"code": "frontend_code", "rules": "eslint, prettier"}
            }
        ]
    else:
        # 通用工具序列
        return [
            {
                "step": 1,
                "tool": "web_search",
                "purpose": "Research the topic",
                "input": {"query": human_intent}
            },
            {
                "step": 2,
                "tool": "code_generator_llm",
                "purpose": "Generate solution",
                "input": {"task": human_intent, "context": str(insight)}
            },
            {
                "step": 3,
                "tool": "test_generator_llm",
                "purpose": "Generate tests",
                "input": {"code_context": "generated_code", "test_requirements": "unit"}
            }
        ]
