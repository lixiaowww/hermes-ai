"""
DebateEngine - 高维生命回看引擎

基于V4.0设计，实现高维生命回看、多角度全面认知和超越时空的智慧洞察。
通过模拟不同生命体、不同时间维度的视角，获得超越当前局限的深刻认知。
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class PerspectiveType(Enum):
    """高维视角类型"""
    TEMPORAL = "temporal"  # 时间维度：过去、现在、未来
    SPATIAL = "spatial"    # 空间维度：微观、宏观、宇宙
    CONSCIOUSNESS = "consciousness"  # 意识维度：个体、集体、宇宙意识
    ENERGY = "energy"      # 能量维度：物质、精神、量子
    WISDOM = "wisdom"      # 智慧维度：经验、直觉、超越

class ReviewStatus(Enum):
    """高维回看状态"""
    INITIATED = "initiated"      # 已启动
    MULTI_DIMENSIONAL = "multi_dimensional"  # 多维度回看中
    TRANSCENDENT = "transcendent"  # 超越维度回看中
    INTEGRATED = "integrated"    # 已整合
    COMPLETED = "completed"      # 已完成

@dataclass
class HighDimensionalInsight:
    """高维洞察"""
    id: str
    perspective_type: PerspectiveType
    life_form: str  # 生命体类型：人类、AI、宇宙意识等
    time_dimension: str  # 时间维度：过去、现在、未来
    space_dimension: str  # 空间维度：微观、宏观、宇宙
    insight_content: str
    wisdom_level: float  # 智慧层次：0-1
    transcendence_score: float  # 超越度：0-1
    timestamp: datetime
    parent_insight_id: Optional[str] = None
    related_insights: List[str] = None

@dataclass
class DimensionalReview:
    """维度回看"""
    dimension_level: int
    insights: List[HighDimensionalInsight]
    synthesis: str  # 该维度的综合洞察
    transcendence_level: float  # 超越层次
    timestamp: datetime
    duration_seconds: float

@dataclass
class TranscendentWisdom:
    """超越智慧"""
    wisdom_integrated: bool
    transcendent_insights: List[str]
    final_wisdom: str
    transcendence_score: float
    universal_principles: List[str]  # 宇宙法则
    timeless_truths: List[str]  # 永恒真理
    timestamp: datetime

@dataclass
class HighDimensionalReview:
    """高维生命回看会话"""
    id: str
    topic: str
    life_forms: List[str]  # 参与的生命体类型
    dimensional_reviews: List[DimensionalReview]
    transcendent_wisdom: Optional[TranscendentWisdom]
    status: ReviewStatus
    created_at: datetime
    updated_at: datetime

class DebateEngine:
    """
    高维生命回看引擎
    
    核心理念：
    1. 高维生命回看 - 从不同生命体、不同时间维度回看问题
    2. 多角度全面认知 - 获得超越当前局限的深刻洞察
    3. 超越时空的智慧 - 整合宇宙法则和永恒真理
    4. 创造性解决方案 - 基于高维认知的创新思路
    
    功能：
    1. 多维度生命体视角模拟
    2. 时间维度的过去-现在-未来回看
    3. 空间维度的微观-宏观-宇宙观察
    4. 意识维度的个体-集体-宇宙意识整合
    5. 超越维度的智慧洞察生成
    """
    
    def __init__(self, max_dimensions: int = 5, transcendence_threshold: float = 0.9):
        self.max_dimensions = max_dimensions
        self.transcendence_threshold = transcendence_threshold
        self.active_reviews: Dict[str, HighDimensionalReview] = {}
        
        # 高维洞察评估权重
        self.insight_weights = {
            PerspectiveType.TEMPORAL: 0.25,
            PerspectiveType.SPATIAL: 0.25,
            PerspectiveType.CONSCIOUSNESS: 0.25,
            PerspectiveType.ENERGY: 0.15,
            PerspectiveType.WISDOM: 0.10
        }
        
        # 生命体类型定义
        self.life_forms = {
            "human": "人类意识 - 理性思维和情感体验",
            "ai": "人工智能 - 逻辑计算和模式识别",
            "collective": "集体意识 - 群体智慧和共识",
            "universal": "宇宙意识 - 超越个体的智慧",
            "quantum": "量子意识 - 不确定性和可能性",
            "transcendent": "超越意识 - 超越时空的智慧"
        }
    
    async def initiate_high_dimensional_review(self, 
                                             topic: str, 
                                             life_forms: List[str],
                                             initial_insights: Optional[Dict[str, str]] = None) -> str:
        """
        发起辩论
        
        Args:
            topic: 辩论主题
            participants: 参与者列表
            initial_arguments: 初始论证（可选）
            
        Returns:
            str: 辩论会话ID
        """
        debate_id = str(uuid.uuid4())
        
        # 创建高维回看会话
        debate_session = HighDimensionalReview(
            id=debate_id,
            topic=topic,
            life_forms=participants,
            dimensional_reviews=[],
            transcendent_wisdom=None,
            status=ReviewStatus.INITIATED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 添加初始论证
        if initial_arguments:
            initial_round = await self._create_initial_round(
                debate_session, initial_arguments
            )
            debate_session.rounds.append(initial_round)
            debate_session.status = DebateStatus.IN_PROGRESS
        
        self.active_debates[debate_id] = debate_session
        
        logger.info(f"Debate initiated: {debate_id} on topic: {topic}")
        return debate_id
    
    async def _create_initial_round(self, 
                                  debate_session: HighDimensionalReview,
                                  initial_arguments: Dict[str, str]) -> DimensionalReview:
        """创建初始轮次"""
        arguments = []
        
        for agent_id, content in initial_arguments.items():
            if agent_id in debate_session.participants:
                argument = Argument(
                    id=str(uuid.uuid4()),
                    agent_id=agent_id,
                    argument_type=ArgumentType.EVIDENCE,
                    content=content,
                    evidence=[],
                    reasoning="Initial position",
                    confidence=0.7,
                    timestamp=datetime.now()
                )
                arguments.append(argument)
        
        return DebateRound(
            round_number=0,
            arguments=arguments,
            summary=f"Initial positions from {len(arguments)} participants",
            timestamp=datetime.now(),
            duration_seconds=0.0
        )
    
    async def add_argument(self, 
                          debate_id: str,
                          agent_id: str,
                          content: str,
                          argument_type: ArgumentType = ArgumentType.REASONING,
                          parent_argument_id: Optional[str] = None) -> str:
        """
        添加论证
        
        Args:
            debate_id: 辩论会话ID
            agent_id: 智能体ID
            content: 论证内容
            argument_type: 论证类型
            parent_argument_id: 父论证ID（用于反驳）
            
        Returns:
            str: 论证ID
        """
        if debate_id not in self.active_debates:
            raise ValueError(f"Debate {debate_id} not found")
        
        debate = self.active_debates[debate_id]
        
        if debate.status != DebateStatus.IN_PROGRESS:
            raise ValueError(f"Debate {debate_id} is not in progress")
        
        if agent_id not in debate.participants:
            raise ValueError(f"Agent {agent_id} is not a participant")
        
        # 创建论证
        argument = Argument(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            argument_type=argument_type,
            content=content,
            evidence=await self._extract_evidence(content),
            reasoning=await self._extract_reasoning(content),
            confidence=await self._calculate_confidence(content, argument_type),
            timestamp=datetime.now(),
            parent_argument_id=parent_argument_id
        )
        
        # 添加到当前轮次
        if not debate.rounds or debate.rounds[-1].round_number >= self.max_rounds:
            # 创建新轮次
            new_round = DebateRound(
                round_number=len(debate.rounds),
                arguments=[argument],
                summary="",
                timestamp=datetime.now(),
                duration_seconds=0.0
            )
            debate.rounds.append(new_round)
        else:
            # 添加到当前轮次
            debate.rounds[-1].arguments.append(argument)
        
        # 更新辩论状态
        debate.updated_at = datetime.now()
        
        # 检查是否应该结束辩论
        await self._check_debate_conclusion(debate)
        
        logger.info(f"Argument added to debate {debate_id} by {agent_id}")
        return argument.id
    
    async def _extract_evidence(self, content: str) -> List[str]:
        """从内容中提取证据"""
        # 简单的证据提取逻辑
        evidence_keywords = [
            'data', 'research', 'study', 'experiment', 'test',
            'statistics', 'analysis', 'results', 'findings',
            'proven', 'demonstrated', 'shown', 'established'
        ]
        
        evidence = []
        sentences = content.split('.')
        
        for sentence in sentences:
            for keyword in evidence_keywords:
                if keyword.lower() in sentence.lower():
                    evidence.append(sentence.strip())
                    break
        
        return evidence
    
    async def _extract_reasoning(self, content: str) -> str:
        """从内容中提取推理过程"""
        # 简单的推理提取逻辑
        reasoning_keywords = [
            'because', 'therefore', 'thus', 'hence', 'consequently',
            'since', 'as', 'due to', 'owing to', 'for this reason'
        ]
        
        for keyword in reasoning_keywords:
            if keyword.lower() in content.lower():
                # 提取包含关键词的句子
                sentences = content.split('.')
                for sentence in sentences:
                    if keyword.lower() in sentence.lower():
                        return sentence.strip()
        
        return "Logical reasoning provided"
    
    async def _calculate_confidence(self, content: str, argument_type: ArgumentType) -> float:
        """计算论证置信度"""
        base_confidence = 0.5
        
        # 基于内容长度
        if len(content) > 100:
            base_confidence += 0.1
        elif len(content) < 50:
            base_confidence -= 0.1
        
        # 基于论证类型
        type_weight = self.argument_weights.get(argument_type, 0.5)
        base_confidence *= type_weight
        
        # 基于关键词密度
        strong_keywords = ['proven', 'demonstrated', 'evidence', 'data', 'research']
        keyword_count = sum(1 for keyword in strong_keywords if keyword in content.lower())
        base_confidence += keyword_count * 0.05
        
        return min(max(base_confidence, 0.0), 1.0)
    
    async def _check_debate_conclusion(self, debate: DebateSession):
        """检查辩论是否应该结束"""
        if not debate.rounds:
            return
        
        current_round = debate.rounds[-1]
        
        # 检查是否达到最大轮次
        if current_round.round_number >= self.max_rounds:
            await self._conclude_debate(debate)
            return
        
        # 检查是否达成共识
        if len(current_round.arguments) >= len(debate.participants):
            consensus_score = await self._calculate_consensus(debate)
            if consensus_score >= self.consensus_threshold:
                await self._conclude_debate(debate)
    
    async def _calculate_consensus(self, debate: DebateSession) -> float:
        """计算共识分数"""
        if not debate.rounds:
            return 0.0
        
        # 简单的共识计算：基于论证相似性
        recent_arguments = debate.rounds[-1].arguments
        if len(recent_arguments) < 2:
            return 0.0
        
        # 计算论证之间的相似性
        similarities = []
        for i, arg1 in enumerate(recent_arguments):
            for arg2 in recent_arguments[i+1:]:
                similarity = await self._calculate_argument_similarity(arg1, arg2)
                similarities.append(similarity)
        
        if not similarities:
            return 0.0
        
        return sum(similarities) / len(similarities)
    
    async def _calculate_argument_similarity(self, arg1: Argument, arg2: Argument) -> float:
        """计算论证相似性"""
        # 简单的相似性计算：基于关键词重叠
        words1 = set(arg1.content.lower().split())
        words2 = set(arg2.content.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    async def _conclude_debate(self, debate: DebateSession):
        """结束辩论"""
        conclusion = await self._generate_conclusion(debate)
        debate.conclusion = conclusion
        debate.status = DebateStatus.CONCLUDED
        debate.updated_at = datetime.now()
        
        logger.info(f"Debate {debate.id} concluded with consensus: {conclusion.consensus_reached}")
    
    async def _generate_conclusion(self, debate: DebateSession) -> DebateConclusion:
        """生成辩论结论"""
        all_arguments = []
        for round_data in debate.rounds:
            all_arguments.extend(round_data.arguments)
        
        if not all_arguments:
            return DebateConclusion(
                consensus_reached=False,
                winning_arguments=[],
                final_position="No arguments provided",
                confidence_score=0.0,
                reasoning="Insufficient data for conclusion",
                timestamp=datetime.now()
            )
        
        # 计算论证强度
        argument_scores = {}
        for argument in all_arguments:
            score = argument.confidence * self.argument_weights.get(argument.argument_type, 0.5)
            if argument.agent_id not in argument_scores:
                argument_scores[argument.agent_id] = []
            argument_scores[argument.agent_id].append(score)
        
        # 计算每个智能体的平均分数
        agent_scores = {}
        for agent_id, scores in argument_scores.items():
            agent_scores[agent_id] = sum(scores) / len(scores)
        
        # 确定获胜者
        if agent_scores:
            winning_agent = max(agent_scores, key=agent_scores.get)
            winning_score = agent_scores[winning_agent]
            
            # 获取获胜者的论证
            winning_arguments = [
                arg.id for arg in all_arguments 
                if arg.agent_id == winning_agent
            ]
            
            # 生成最终立场
            winning_arg_contents = [
                arg.content for arg in all_arguments 
                if arg.agent_id == winning_agent
            ]
            final_position = " ".join(winning_arg_contents[:3])  # 取前3个论证
            
            consensus_reached = winning_score >= self.consensus_threshold
            
            return DebateConclusion(
                consensus_reached=consensus_reached,
                winning_arguments=winning_arguments,
                final_position=final_position,
                confidence_score=winning_score,
                reasoning=f"Based on {len(all_arguments)} arguments from {len(debate.participants)} participants",
                timestamp=datetime.now()
            )
        else:
            return DebateConclusion(
                consensus_reached=False,
                winning_arguments=[],
                final_position="No valid arguments found",
                confidence_score=0.0,
                reasoning="No valid arguments to evaluate",
                timestamp=datetime.now()
            )
    
    async def get_debate_status(self, debate_id: str) -> Optional[Dict[str, Any]]:
        """获取辩论状态"""
        if debate_id not in self.active_debates:
            return None
        
        debate = self.active_debates[debate_id]
        
        return {
            "id": debate.id,
            "topic": debate.topic,
            "participants": debate.participants,
            "status": debate.status.value,
            "rounds_count": len(debate.rounds),
            "created_at": debate.created_at.isoformat(),
            "updated_at": debate.updated_at.isoformat(),
            "conclusion": {
                "consensus_reached": debate.conclusion.consensus_reached if debate.conclusion else False,
                "confidence_score": debate.conclusion.confidence_score if debate.conclusion else 0.0,
                "final_position": debate.conclusion.final_position if debate.conclusion else None
            } if debate.conclusion else None
        }
    
    async def get_debate_rounds(self, debate_id: str) -> Optional[List[Dict[str, Any]]]:
        """获取辩论轮次"""
        if debate_id not in self.active_debates:
            return None
        
        debate = self.active_debates[debate_id]
        
        rounds_data = []
        for round_data in debate.rounds:
            arguments_data = []
            for argument in round_data.arguments:
                arguments_data.append({
                    "id": argument.id,
                    "agent_id": argument.agent_id,
                    "type": argument.argument_type.value,
                    "content": argument.content,
                    "evidence": argument.evidence,
                    "reasoning": argument.reasoning,
                    "confidence": argument.confidence,
                    "timestamp": argument.timestamp.isoformat(),
                    "parent_argument_id": argument.parent_argument_id
                })
            
            rounds_data.append({
                "round_number": round_data.round_number,
                "arguments": arguments_data,
                "summary": round_data.summary,
                "timestamp": round_data.timestamp.isoformat(),
                "duration_seconds": round_data.duration_seconds
            })
        
        return rounds_data
    
    async def list_active_debates(self) -> List[Dict[str, Any]]:
        """列出活跃的辩论"""
        debates = []
        for debate in self.active_debates.values():
            debates.append({
                "id": debate.id,
                "topic": debate.topic,
                "participants": debate.participants,
                "status": debate.status.value,
                "rounds_count": len(debate.rounds),
                "created_at": debate.created_at.isoformat()
            })
        
        return debates

# 全局实例
debate_engine = DebateEngine()
