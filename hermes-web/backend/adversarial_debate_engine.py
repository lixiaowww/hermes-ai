"""
AdversarialDebateEngine - 对抗性思辨引擎

基于V4.0设计，实现对抗性思辨、观点碰撞和真理发现。
通过正反双方的激烈辩论，在逻辑对抗中发现最优解决方案。
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

class ArgumentType(Enum):
    """论证类型"""
    EVIDENCE = "evidence"        # 证据
    REASONING = "reasoning"      # 推理
    COUNTER_ARGUMENT = "counter_argument"  # 反驳
    CONCLUSION = "conclusion"    # 结论
    ASSUMPTION = "assumption"    # 假设

class DebateStatus(Enum):
    """辩论状态"""
    INITIATED = "initiated"      # 已启动
    IN_PROGRESS = "in_progress"  # 进行中
    CONCLUDED = "concluded"      # 已结束
    ABANDONED = "abandoned"      # 已放弃

class DebateSide(Enum):
    """辩论方"""
    PRO = "pro"          # 正方
    CON = "con"          # 反方
    MODERATOR = "moderator"  # 主持人

@dataclass
class Argument:
    """论证结构"""
    id: str
    side: DebateSide
    argument_type: ArgumentType
    content: str
    evidence: List[str]
    reasoning: str
    confidence: float
    timestamp: datetime
    parent_argument_id: Optional[str] = None
    counter_arguments: List[str] = None
    logical_strength: float = 0.0  # 逻辑强度
    emotional_impact: float = 0.0  # 情感影响

@dataclass
class DebateRound:
    """辩论轮次"""
    round_number: int
    arguments: List[Argument]
    summary: str
    timestamp: datetime
    duration_seconds: float
    intensity_score: float  # 激烈程度

@dataclass
class DebateConclusion:
    """辩论结论"""
    consensus_reached: bool
    winning_side: Optional[DebateSide]
    winning_arguments: List[str]
    final_position: str
    confidence_score: float
    reasoning: str
    key_insights: List[str]  # 关键洞察
    remaining_disagreements: List[str]  # 剩余分歧
    timestamp: datetime

@dataclass
class DebateSession:
    """对抗性思辨会话"""
    id: str
    topic: str
    pro_side: str  # 正方代表
    con_side: str  # 反方代表
    moderator: str  # 主持人
    rounds: List[DebateRound]
    conclusion: Optional[DebateConclusion]
    status: DebateStatus
    created_at: datetime
    updated_at: datetime
    intensity_level: float = 0.0  # 整体激烈程度

class AdversarialDebateEngine:
    """
    对抗性思辨引擎
    
    核心理念：
    1. 对抗性思辨 - 通过正反双方激烈辩论发现真理
    2. 观点碰撞 - 不同观点的直接对抗和碰撞
    3. 逻辑对抗 - 基于逻辑和证据的理性对抗
    4. 真理发现 - 在对抗中逐步接近最优解决方案
    
    功能：
    1. 正反双方辩论管理
    2. 论证强度评估
    3. 逻辑漏洞检测
    4. 共识达成机制
    5. 关键洞察提取
    """
    
    def __init__(self, max_rounds: int = 5, consensus_threshold: float = 0.8):
        self.max_rounds = max_rounds
        self.consensus_threshold = consensus_threshold
        self.active_debates: Dict[str, DebateSession] = {}
        
        # 论证质量评估权重
        self.argument_weights = {
            ArgumentType.EVIDENCE: 0.3,
            ArgumentType.REASONING: 0.4,
            ArgumentType.COUNTER_ARGUMENT: 0.2,
            ArgumentType.CONCLUSION: 0.1
        }
        
        # 辩论强度评估因子
        self.intensity_factors = {
            "logical_conflict": 0.4,      # 逻辑冲突
            "evidence_contradiction": 0.3, # 证据矛盾
            "emotional_charge": 0.2,      # 情感强度
            "stakes_level": 0.1           # 利害关系
        }
    
    async def initiate_debate(self, 
                            topic: str, 
                            pro_side: str,
                            con_side: str,
                            moderator: str = "system",
                            initial_arguments: Optional[Dict[str, str]] = None) -> str:
        """
        发起对抗性思辨
        
        Args:
            topic: 辩论主题
            pro_side: 正方代表
            con_side: 反方代表
            moderator: 主持人
            initial_arguments: 初始论证（可选）
            
        Returns:
            str: 辩论ID
        """
        debate_id = str(uuid.uuid4())
        
        # 创建对抗性思辨会话
        debate_session = DebateSession(
            id=debate_id,
            topic=topic,
            pro_side=pro_side,
            con_side=con_side,
            moderator=moderator,
            rounds=[],
            conclusion=None,
            status=DebateStatus.INITIATED,
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
        
        logger.info(f"Adversarial debate initiated: {debate_id} on topic: {topic}")
        return debate_id
    
    async def add_argument(self, 
                          debate_id: str,
                          side: DebateSide,
                          content: str,
                          argument_type: ArgumentType = ArgumentType.REASONING,
                          parent_argument_id: Optional[str] = None) -> str:
        """
        添加论证
        
        Args:
            debate_id: 辩论ID
            side: 辩论方
            content: 论证内容
            argument_type: 论证类型
            parent_argument_id: 父论证ID
            
        Returns:
            str: 论证ID
        """
        if debate_id not in self.active_debates:
            raise ValueError(f"Debate {debate_id} not found")
        
        debate = self.active_debates[debate_id]
        
        if debate.status != DebateStatus.IN_PROGRESS:
            raise ValueError(f"Debate {debate_id} is not in progress")
        
        # 创建论证
        argument = Argument(
            id=str(uuid.uuid4()),
            side=side,
            argument_type=argument_type,
            content=content,
            evidence=await self._extract_evidence(content),
            reasoning=await self._extract_reasoning(content),
            confidence=await self._calculate_confidence(content, argument_type),
            timestamp=datetime.now(),
            parent_argument_id=parent_argument_id,
            logical_strength=await self._calculate_logical_strength(content),
            emotional_impact=await self._calculate_emotional_impact(content)
        )
        
        # 添加到当前轮次
        if not debate.rounds or len(debate.rounds[-1].arguments) >= 2:
            # 创建新轮次
            new_round = DebateRound(
                round_number=len(debate.rounds) + 1,
                arguments=[],
                summary="",
                timestamp=datetime.now(),
                duration_seconds=0.0,
                intensity_score=0.0
            )
            debate.rounds.append(new_round)
        
        current_round = debate.rounds[-1]
        current_round.arguments.append(argument)
        
        # 更新轮次摘要和强度
        current_round.summary = await self._summarize_round(current_round.arguments)
        current_round.intensity_score = await self._calculate_round_intensity(current_round.arguments)
        
        # 检查是否达到最大轮次
        if len(debate.rounds) >= self.max_rounds:
            await self._conclude_debate(debate_id)
        
        debate.updated_at = datetime.now()
        
        logger.info(f"Argument added to debate {debate_id}: {argument.id}")
        return argument.id
    
    async def _create_initial_round(self, 
                                  debate_session: DebateSession,
                                  initial_arguments: Dict[str, str]) -> DebateRound:
        """创建初始轮次"""
        arguments = []
        
        # 处理正方初始论证
        if "pro" in initial_arguments:
            pro_argument = Argument(
                id=str(uuid.uuid4()),
                side=DebateSide.PRO,
                argument_type=ArgumentType.REASONING,
                content=initial_arguments["pro"],
                evidence=await self._extract_evidence(initial_arguments["pro"]),
                reasoning=await self._extract_reasoning(initial_arguments["pro"]),
                confidence=await self._calculate_confidence(initial_arguments["pro"], ArgumentType.REASONING),
                timestamp=datetime.now(),
                logical_strength=await self._calculate_logical_strength(initial_arguments["pro"]),
                emotional_impact=await self._calculate_emotional_impact(initial_arguments["pro"])
            )
            arguments.append(pro_argument)
        
        # 处理反方初始论证
        if "con" in initial_arguments:
            con_argument = Argument(
                id=str(uuid.uuid4()),
                side=DebateSide.CON,
                argument_type=ArgumentType.REASONING,
                content=initial_arguments["con"],
                evidence=await self._extract_evidence(initial_arguments["con"]),
                reasoning=await self._extract_reasoning(initial_arguments["con"]),
                confidence=await self._calculate_confidence(initial_arguments["con"], ArgumentType.REASONING),
                timestamp=datetime.now(),
                logical_strength=await self._calculate_logical_strength(initial_arguments["con"]),
                emotional_impact=await self._calculate_emotional_impact(initial_arguments["con"])
            )
            arguments.append(con_argument)
        
        return DebateRound(
            round_number=1,
            arguments=arguments,
            summary=await self._summarize_round(arguments),
            timestamp=datetime.now(),
            duration_seconds=0.0,
            intensity_score=await self._calculate_round_intensity(arguments)
        )
    
    async def _extract_evidence(self, content: str) -> List[str]:
        """提取证据"""
        # 简单的证据提取逻辑
        evidence = []
        if "数据" in content or "data" in content.lower():
            evidence.append("数据支持")
        if "研究" in content or "research" in content.lower():
            evidence.append("研究证据")
        if "案例" in content or "case" in content.lower():
            evidence.append("案例分析")
        return evidence
    
    async def _extract_reasoning(self, content: str) -> str:
        """提取推理过程"""
        # 简单的推理提取
        if "因为" in content or "because" in content.lower():
            return "因果推理"
        elif "如果" in content or "if" in content.lower():
            return "条件推理"
        elif "因此" in content or "therefore" in content.lower():
            return "结论推理"
        else:
            return "一般推理"
    
    async def _calculate_confidence(self, content: str, argument_type: ArgumentType) -> float:
        """计算置信度"""
        base_confidence = 0.5
        
        # 基于论证类型调整
        if argument_type == ArgumentType.EVIDENCE:
            base_confidence += 0.2
        elif argument_type == ArgumentType.REASONING:
            base_confidence += 0.1
        
        # 基于内容长度调整
        if len(content) > 100:
            base_confidence += 0.1
        
        # 基于关键词调整
        confidence_keywords = ["证明", "证实", "证据", "数据", "研究", "实验"]
        for keyword in confidence_keywords:
            if keyword in content:
                base_confidence += 0.05
        
        return min(base_confidence, 1.0)
    
    async def _calculate_logical_strength(self, content: str) -> float:
        """计算逻辑强度"""
        strength = 0.5
        
        # 逻辑连接词
        logical_connectors = ["因为", "所以", "因此", "如果", "那么", "但是", "然而"]
        for connector in logical_connectors:
            if connector in content:
                strength += 0.1
        
        # 量化表达
        quantifiers = ["所有", "大部分", "通常", "经常", "很少", "从不"]
        for quantifier in quantifiers:
            if quantifier in content:
                strength += 0.05
        
        return min(strength, 1.0)
    
    async def _calculate_emotional_impact(self, content: str) -> float:
        """计算情感影响"""
        impact = 0.3
        
        # 情感词汇
        emotional_words = ["重要", "关键", "严重", "危险", "机会", "优势", "劣势"]
        for word in emotional_words:
            if word in content:
                impact += 0.1
        
        # 感叹号
        if "!" in content or "！" in content:
            impact += 0.2
        
        return min(impact, 1.0)
    
    async def _summarize_round(self, arguments: List[Argument]) -> str:
        """总结轮次"""
        if not arguments:
            return "No arguments in this round"
        
        pro_args = [arg for arg in arguments if arg.side == DebateSide.PRO]
        con_args = [arg for arg in arguments if arg.side == DebateSide.CON]
        
        summary_parts = []
        
        if pro_args:
            summary_parts.append(f"正方观点: {pro_args[0].content[:100]}...")
        
        if con_args:
            summary_parts.append(f"反方观点: {con_args[0].content[:100]}...")
        
        return " | ".join(summary_parts)
    
    async def _calculate_round_intensity(self, arguments: List[Argument]) -> float:
        """计算轮次激烈程度"""
        if not arguments:
            return 0.0
        
        # 基于论证数量和强度
        total_intensity = sum(arg.logical_strength + arg.emotional_impact for arg in arguments)
        avg_intensity = total_intensity / len(arguments)
        
        # 基于观点对立程度
        pro_args = [arg for arg in arguments if arg.side == DebateSide.PRO]
        con_args = [arg for arg in arguments if arg.side == DebateSide.CON]
        
        if pro_args and con_args:
            # 计算观点对立程度
            pro_avg = sum(arg.confidence for arg in pro_args) / len(pro_args)
            con_avg = sum(arg.confidence for arg in con_args) / len(con_args)
            opposition = abs(pro_avg - con_avg)
            avg_intensity += opposition * 0.3
        
        return min(avg_intensity, 1.0)
    
    async def _conclude_debate(self, debate_id: str) -> DebateConclusion:
        """结束辩论并生成结论"""
        debate = self.active_debates[debate_id]
        
        # 收集所有论证
        all_arguments = []
        for round in debate.rounds:
            all_arguments.extend(round.arguments)
        
        # 分析正反双方
        pro_arguments = [arg for arg in all_arguments if arg.side == DebateSide.PRO]
        con_arguments = [arg for arg in all_arguments if arg.side == DebateSide.CON]
        
        # 计算双方强度
        pro_strength = sum(arg.confidence * arg.logical_strength for arg in pro_arguments)
        con_strength = sum(arg.confidence * arg.logical_strength for arg in con_arguments)
        
        # 判断获胜方
        if pro_strength > con_strength * 1.2:
            winning_side = DebateSide.PRO
            consensus_reached = True
        elif con_strength > pro_strength * 1.2:
            winning_side = DebateSide.CON
            consensus_reached = True
        else:
            winning_side = None
            consensus_reached = False
        
        # 生成关键洞察
        key_insights = await self._extract_key_insights(all_arguments)
        
        # 识别剩余分歧
        remaining_disagreements = await self._identify_disagreements(pro_arguments, con_arguments)
        
        # 生成最终结论
        conclusion = DebateConclusion(
            consensus_reached=consensus_reached,
            winning_side=winning_side,
            winning_arguments=[arg.id for arg in (pro_arguments if winning_side == DebateSide.PRO else con_arguments)],
            final_position=await self._generate_final_position(winning_side, key_insights),
            confidence_score=max(pro_strength, con_strength) / max(len(pro_arguments), len(con_arguments), 1),
            reasoning=await self._generate_reasoning(pro_strength, con_strength, consensus_reached),
            key_insights=key_insights,
            remaining_disagreements=remaining_disagreements,
            timestamp=datetime.now()
        )
        
        debate.conclusion = conclusion
        debate.status = DebateStatus.CONCLUDED
        debate.updated_at = datetime.now()
        
        logger.info(f"Debate {debate_id} concluded with consensus: {consensus_reached}")
        return conclusion
    
    async def _extract_key_insights(self, arguments: List[Argument]) -> List[str]:
        """提取关键洞察"""
        insights = []
        
        # 基于高置信度论证提取洞察
        high_confidence_args = [arg for arg in arguments if arg.confidence > 0.8]
        for arg in high_confidence_args[:3]:  # 取前3个
            insights.append(f"【{arg.side.value.upper()}】{arg.content[:50]}...")
        
        return insights
    
    async def _identify_disagreements(self, pro_args: List[Argument], con_args: List[Argument]) -> List[str]:
        """识别剩余分歧"""
        disagreements = []
        
        if pro_args and con_args:
            disagreements.append("核心观点存在根本分歧")
            disagreements.append("证据解释方式不同")
            disagreements.append("价值判断标准不同")
        
        return disagreements
    
    async def _generate_final_position(self, winning_side: Optional[DebateSide], insights: List[str]) -> str:
        """生成最终立场"""
        if winning_side == DebateSide.PRO:
            return f"正方观点更具说服力。关键洞察：{', '.join(insights[:2])}"
        elif winning_side == DebateSide.CON:
            return f"反方观点更具说服力。关键洞察：{', '.join(insights[:2])}"
        else:
            return f"双方观点势均力敌，需要进一步讨论。关键洞察：{', '.join(insights[:2])}"
    
    async def _generate_reasoning(self, pro_strength: float, con_strength: float, consensus: bool) -> str:
        """生成推理过程"""
        if consensus:
            if pro_strength > con_strength:
                return f"正方论证强度({pro_strength:.2f})明显超过反方({con_strength:.2f})，达成共识。"
            else:
                return f"反方论证强度({con_strength:.2f})明显超过正方({pro_strength:.2f})，达成共识。"
        else:
            return f"双方论证强度接近(正方:{pro_strength:.2f}, 反方:{con_strength:.2f})，未达成共识。"
    
    async def get_debate_status(self, debate_id: str) -> Optional[Dict[str, Any]]:
        """获取辩论状态"""
        if debate_id not in self.active_debates:
            return None
        
        debate = self.active_debates[debate_id]
        
        return {
            "id": debate.id,
            "topic": debate.topic,
            "pro_side": debate.pro_side,
            "con_side": debate.con_side,
            "moderator": debate.moderator,
            "status": debate.status.value,
            "rounds_count": len(debate.rounds),
            "total_arguments": sum(len(round.arguments) for round in debate.rounds),
            "intensity_level": debate.intensity_level,
            "conclusion_available": debate.conclusion is not None,
            "created_at": debate.created_at.isoformat(),
            "updated_at": debate.updated_at.isoformat()
        }
    
    async def get_debate_conclusion(self, debate_id: str) -> Optional[Dict[str, Any]]:
        """获取辩论结论"""
        if debate_id not in self.active_debates:
            return None
        
        debate = self.active_debates[debate_id]
        
        if not debate.conclusion:
            return None
        
        conclusion = debate.conclusion
        return {
            "consensus_reached": conclusion.consensus_reached,
            "winning_side": conclusion.winning_side.value if conclusion.winning_side else None,
            "winning_arguments": conclusion.winning_arguments,
            "final_position": conclusion.final_position,
            "confidence_score": conclusion.confidence_score,
            "reasoning": conclusion.reasoning,
            "key_insights": conclusion.key_insights,
            "remaining_disagreements": conclusion.remaining_disagreements,
            "timestamp": conclusion.timestamp.isoformat()
        }

# 全局实例
adversarial_debate_engine = AdversarialDebateEngine()
