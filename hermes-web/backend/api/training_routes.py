"""
Training Module API Routes
松耦合的训练模块API路由
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional

from core.models import FeedbackRequest, InteractionRecordRequest
from services.auth_service import get_current_user
from training_module import training_module, FeedbackType

router = APIRouter(prefix="/training", tags=["training"])

@router.post("/record-interaction")
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
        raise HTTPException(status_code=500, detail=f"Failed to record interaction: {str(e)}")

@router.post("/add-feedback")
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
        raise HTTPException(status_code=500, detail=f"Failed to add feedback: {str(e)}")

@router.get("/insights")
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
        raise HTTPException(status_code=500, detail=f"Failed to get learning insights: {str(e)}")

@router.get("/metrics")
async def get_performance_metrics_api(
    current_user: dict = Depends(get_current_user)
):
    """获取性能指标"""
    try:
        metrics = await training_module.get_performance_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

@router.post("/optimize-prompt")
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
        raise HTTPException(status_code=500, detail=f"Failed to optimize prompt: {str(e)}")
