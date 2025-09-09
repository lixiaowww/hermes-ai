"""
Core Module API Routes
松耦合的核心模块API路由
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional

from core.models import (
    MeditationRequest, MeditationResponse,
    DebateInitiateRequest, DebateArgumentRequest, DebateResponse,
    HighDimensionalAnalysisRequest, HighDimensionalReviewRequest, DimensionalInsightRequest
)
from services.auth_service import get_current_user
from meditation_module import meditation_module
from adversarial_debate_engine import adversarial_debate_engine, ArgumentType, DebateSide
from high_dimensional_analysis_module import high_dimensional_analysis_module
from high_dimensional_review_engine import high_dimensional_review_engine, PerspectiveType

router = APIRouter(prefix="/core-modules", tags=["core-modules"])

# ========================= 禅定模块路由 =========================
@router.post("/meditation/frame", response_model=MeditationResponse)
async def meditation_frame(
    request: MeditationRequest,
    current_user: dict = Depends(get_current_user)
):
    """问题框架化 - 生成核心洞见报告"""
    try:
        from datetime import datetime
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
        return MeditationResponse(
            success=False,
            error=str(e),
            processing_time=None
        )

# ========================= 高维生命回看路由 =========================
@router.post("/high-dimensional-review/initiate")
async def initiate_high_dimensional_review(
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
        raise HTTPException(status_code=500, detail=f"Failed to initiate high-dimensional review: {str(e)}")

@router.post("/high-dimensional-review/add-insight")
async def add_dimensional_insight(
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
        raise HTTPException(status_code=500, detail=f"Failed to add dimensional insight: {str(e)}")

# ========================= 高维分析模块路由 =========================
@router.post("/high-dimensional-analysis/analyze")
async def analyze_codebase_high_dimensional(
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
        raise HTTPException(status_code=500, detail=f"High-dimensional analysis failed: {str(e)}")

@router.get("/high-dimensional-analysis/{analysis_id}/report")
async def get_analysis_report(
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
        raise HTTPException(status_code=500, detail=f"Failed to get analysis report: {str(e)}")

# ========================= 高维生命回看路由 =========================
@router.post("/high-dimensional-review/initiate")
async def initiate_high_dimensional_review(
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
        raise HTTPException(status_code=500, detail=f"Failed to initiate high-dimensional review: {str(e)}")

@router.post("/high-dimensional-review/add-insight")
async def add_dimensional_insight(
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
        raise HTTPException(status_code=500, detail=f"Failed to add dimensional insight: {str(e)}")

@router.post("/high-dimensional-review/generate-wisdom/{review_id}")
async def generate_transcendent_wisdom(
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
        raise HTTPException(status_code=500, detail=f"Failed to generate transcendent wisdom: {str(e)}")

@router.get("/high-dimensional-review/{review_id}/status")
async def get_review_status(
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
        raise HTTPException(status_code=500, detail=f"Failed to get review status: {str(e)}")

@router.get("/high-dimensional-review/active")
async def list_active_reviews(
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
        raise HTTPException(status_code=500, detail=f"Failed to list active reviews: {str(e)}")
