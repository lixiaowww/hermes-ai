"""
TrainingModule - Hermes AI 学习训练模块

通过交互结果和人类反馈来持续改善prompt质量和协调效果
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import uuid
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

class FeedbackType(Enum):
    """反馈类型"""
    HUMAN_RATING = "human_rating"  # 人类评分
    OUTCOME_QUALITY = "outcome_quality"  # 结果质量
    TOOL_EFFECTIVENESS = "tool_effectiveness"  # 工具有效性
    ALIGNMENT_SCORE = "alignment_score"  # 对齐度评分
    USER_SATISFACTION = "user_satisfaction"  # 用户满意度

class LearningPhase(Enum):
    """学习阶段"""
    DATA_COLLECTION = "data_collection"  # 数据收集
    PATTERN_ANALYSIS = "pattern_analysis"  # 模式分析
    PROMPT_OPTIMIZATION = "prompt_optimization"  # Prompt优化
    MODEL_ADAPTATION = "model_adaptation"  # 模型适应

@dataclass
class InteractionRecord:
    """交互记录"""
    id: str
    user_intent: str
    original_prompt: str
    orchestration_plan: List[Dict[str, Any]]
    tool_calls: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    final_outcome: Dict[str, Any]
    human_feedback: Optional[Dict[str, Any]] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    learning_phase: LearningPhase = LearningPhase.DATA_COLLECTION

@dataclass
class PromptTemplate:
    """Prompt模板"""
    id: str
    name: str
    category: str  # meditation, orchestration, tool_coordination
    template: str
    variables: List[str]
    performance_score: float
    usage_count: int
    success_rate: float
    last_updated: datetime

@dataclass
class LearningInsight:
    """学习洞察"""
    id: str
    pattern_type: str
    description: str
    confidence: float
    applicable_scenarios: List[str]
    improvement_suggestions: List[str]
    evidence_count: int

class TrainingModule:
    """
    Hermes AI 训练模块
    
    功能：
    1. 收集交互数据和人类反馈
    2. 分析成功模式和失败原因
    3. 优化prompt模板和协调策略
    4. 持续改善AI对齐效果
    """
    
    def __init__(self, db_path: str = "hermes_training.db"):
        self.db_path = db_path
        self._init_database()
        self.prompt_templates = {}
        self.learning_insights = []
        self._load_existing_data()
    
    def _init_database(self):
        """初始化训练数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 交互记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interaction_records (
                id TEXT PRIMARY KEY,
                user_intent TEXT,
                original_prompt TEXT,
                orchestration_plan TEXT,
                tool_calls TEXT,
                tool_results TEXT,
                final_outcome TEXT,
                human_feedback TEXT,
                quality_metrics TEXT,
                timestamp TEXT,
                learning_phase TEXT
            )
        ''')
        
        # Prompt模板表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompt_templates (
                id TEXT PRIMARY KEY,
                name TEXT,
                category TEXT,
                template TEXT,
                variables TEXT,
                performance_score REAL,
                usage_count INTEGER,
                success_rate REAL,
                last_updated TEXT
            )
        ''')
        
        # 学习洞察表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_insights (
                id TEXT PRIMARY KEY,
                pattern_type TEXT,
                description TEXT,
                confidence REAL,
                applicable_scenarios TEXT,
                improvement_suggestions TEXT,
                evidence_count INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_existing_data(self):
        """加载现有数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 加载prompt模板
        cursor.execute('SELECT * FROM prompt_templates')
        for row in cursor.fetchall():
            template = PromptTemplate(
                id=row[0],
                name=row[1],
                category=row[2],
                template=row[3],
                variables=json.loads(row[4]),
                performance_score=row[5],
                usage_count=row[6],
                success_rate=row[7],
                last_updated=datetime.fromisoformat(row[8])
            )
            self.prompt_templates[template.id] = template
        
        # 加载学习洞察
        cursor.execute('SELECT * FROM learning_insights')
        for row in cursor.fetchall():
            insight = LearningInsight(
                id=row[0],
                pattern_type=row[1],
                description=row[2],
                confidence=row[3],
                applicable_scenarios=json.loads(row[4]),
                improvement_suggestions=json.loads(row[5]),
                evidence_count=row[6]
            )
            self.learning_insights.append(insight)
        
        conn.close()
    
    async def record_interaction(self, 
                               user_intent: str,
                               original_prompt: str,
                               orchestration_plan: List[Dict[str, Any]],
                               tool_calls: List[Dict[str, Any]],
                               tool_results: List[Dict[str, Any]],
                               final_outcome: Dict[str, Any]) -> str:
        """记录交互过程"""
        interaction_id = str(uuid.uuid4())
        
        record = InteractionRecord(
            id=interaction_id,
            user_intent=user_intent,
            original_prompt=original_prompt,
            orchestration_plan=orchestration_plan,
            tool_calls=tool_calls,
            tool_results=tool_results,
            final_outcome=final_outcome,
            timestamp=datetime.now(),
            learning_phase=LearningPhase.DATA_COLLECTION
        )
        
        # 保存到数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO interaction_records 
            (id, user_intent, original_prompt, orchestration_plan, tool_calls, 
             tool_results, final_outcome, human_feedback, quality_metrics, 
             timestamp, learning_phase)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.id,
            record.user_intent,
            record.original_prompt,
            json.dumps(record.orchestration_plan),
            json.dumps(record.tool_calls),
            json.dumps(record.tool_results),
            json.dumps(record.final_outcome),
            json.dumps(record.human_feedback) if record.human_feedback else None,
            json.dumps(record.quality_metrics) if record.quality_metrics else None,
            record.timestamp.isoformat(),
            record.learning_phase.value
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Recorded interaction: {interaction_id}")
        return interaction_id
    
    async def add_human_feedback(self, 
                               interaction_id: str,
                               feedback_type: FeedbackType,
                               rating: float,
                               comments: str = "",
                               specific_improvements: List[str] = None) -> bool:
        """添加人类反馈"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取现有记录
            cursor.execute('SELECT human_feedback FROM interaction_records WHERE id = ?', (interaction_id,))
            result = cursor.fetchone()
            
            if not result:
                return False
            
            # 更新反馈
            existing_feedback = json.loads(result[0]) if result[0] else {}
            existing_feedback[feedback_type.value] = {
                "rating": rating,
                "comments": comments,
                "specific_improvements": specific_improvements or [],
                "timestamp": datetime.now().isoformat()
            }
            
            cursor.execute('''
                UPDATE interaction_records 
                SET human_feedback = ? 
                WHERE id = ?
            ''', (json.dumps(existing_feedback), interaction_id))
            
            conn.commit()
            conn.close()
            
            # 触发学习分析
            await self._trigger_learning_analysis(interaction_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add human feedback: {e}")
            return False
    
    async def _trigger_learning_analysis(self, interaction_id: str):
        """触发学习分析"""
        logger.info(f"Triggering learning analysis for interaction: {interaction_id}")
        
        # 分析交互模式
        await self._analyze_interaction_patterns(interaction_id)
        
        # 优化prompt模板
        await self._optimize_prompt_templates(interaction_id)
        
        # 更新协调策略
        await self._update_orchestration_strategies(interaction_id)
    
    async def _analyze_interaction_patterns(self, interaction_id: str):
        """分析交互模式"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取交互记录
        cursor.execute('SELECT * FROM interaction_records WHERE id = ?', (interaction_id,))
        result = cursor.fetchone()
        
        if not result:
            return
        
        # 分析成功模式
        success_patterns = await self._identify_success_patterns(result)
        
        # 分析失败原因
        failure_patterns = await self._identify_failure_patterns(result)
        
        # 生成学习洞察
        insights = await self._generate_learning_insights(success_patterns, failure_patterns)
        
        # 保存洞察
        for insight in insights:
            cursor.execute('''
                INSERT OR REPLACE INTO learning_insights 
                (id, pattern_type, description, confidence, applicable_scenarios, 
                 improvement_suggestions, evidence_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                insight.id,
                insight.pattern_type,
                insight.description,
                insight.confidence,
                json.dumps(insight.applicable_scenarios),
                json.dumps(insight.improvement_suggestions),
                insight.evidence_count
            ))
        
        conn.commit()
        conn.close()
    
    async def _identify_success_patterns(self, interaction_record) -> List[Dict[str, Any]]:
        """识别成功模式"""
        patterns = []
        
        # 分析高评分交互
        human_feedback = json.loads(interaction_record[7]) if interaction_record[7] else {}
        
        if human_feedback.get('human_rating', {}).get('rating', 0) >= 4.0:
            patterns.append({
                "type": "high_rating_pattern",
                "description": "高评分交互模式",
                "confidence": 0.8,
                "characteristics": [
                    "用户意图清晰",
                    "工具选择恰当",
                    "结果质量高",
                    "用户满意度高"
                ]
            })
        
        return patterns
    
    async def _identify_failure_patterns(self, interaction_record) -> List[Dict[str, Any]]:
        """识别失败模式"""
        patterns = []
        
        # 分析低评分交互
        human_feedback = json.loads(interaction_record[7]) if interaction_record[7] else {}
        
        if human_feedback.get('human_rating', {}).get('rating', 0) < 3.0:
            patterns.append({
                "type": "low_rating_pattern",
                "description": "低评分交互模式",
                "confidence": 0.8,
                "characteristics": [
                    "用户意图理解偏差",
                    "工具选择不当",
                    "结果质量低",
                    "用户满意度低"
                ]
            })
        
        return patterns
    
    async def _generate_learning_insights(self, success_patterns: List[Dict], failure_patterns: List[Dict]) -> List[LearningInsight]:
        """生成学习洞察"""
        insights = []
        
        for pattern in success_patterns:
            insight = LearningInsight(
                id=str(uuid.uuid4()),
                pattern_type=pattern["type"],
                description=pattern["description"],
                confidence=pattern["confidence"],
                applicable_scenarios=pattern["characteristics"],
                improvement_suggestions=[
                    "保持这种模式",
                    "在类似场景中应用",
                    "进一步优化细节"
                ],
                evidence_count=1
            )
            insights.append(insight)
        
        for pattern in failure_patterns:
            insight = LearningInsight(
                id=str(uuid.uuid4()),
                pattern_type=pattern["type"],
                description=pattern["description"],
                confidence=pattern["confidence"],
                applicable_scenarios=pattern["characteristics"],
                improvement_suggestions=[
                    "避免这种模式",
                    "改进意图理解",
                    "优化工具选择",
                    "提升结果质量"
                ],
                evidence_count=1
            )
            insights.append(insight)
        
        return insights
    
    async def _optimize_prompt_templates(self, interaction_id: str):
        """优化prompt模板"""
        # 基于交互结果优化模板
        logger.info(f"Optimizing prompt templates based on interaction: {interaction_id}")
        
        # 这里可以实现具体的优化逻辑
        # 例如：调整模板参数、添加新的变量、修改模板结构等
    
    async def _update_orchestration_strategies(self, interaction_id: str):
        """更新协调策略"""
        # 基于交互结果更新协调策略
        logger.info(f"Updating orchestration strategies based on interaction: {interaction_id}")
        
        # 这里可以实现具体的策略更新逻辑
        # 例如：调整工具选择算法、优化协调顺序、改进质量评估等
    
    async def get_optimized_prompt(self, 
                                 category: str,
                                 context: Dict[str, Any],
                                 user_intent: str) -> str:
        """获取优化的prompt"""
        # 根据类别和上下文选择最佳模板
        best_template = None
        best_score = 0.0
        
        for template in self.prompt_templates.values():
            if template.category == category:
                # 计算模板适用性分数
                score = self._calculate_template_score(template, context, user_intent)
                if score > best_score:
                    best_score = score
                    best_template = template
        
        if best_template:
            # 使用模板生成prompt
            return self._generate_prompt_from_template(best_template, context, user_intent)
        else:
            # 使用默认模板
            return self._generate_default_prompt(category, context, user_intent)
    
    def _calculate_template_score(self, template: PromptTemplate, context: Dict[str, Any], user_intent: str) -> float:
        """计算模板适用性分数"""
        score = template.performance_score * 0.4
        score += template.success_rate * 0.3
        score += template.usage_count * 0.1
        
        # 基于上下文的匹配度
        context_match = self._calculate_context_match(template, context)
        score += context_match * 0.2
        
        return score
    
    def _calculate_context_match(self, template: PromptTemplate, context: Dict[str, Any]) -> float:
        """计算上下文匹配度"""
        # 简单的匹配度计算
        match_score = 0.0
        
        for variable in template.variables:
            if variable in context:
                match_score += 0.2
        
        return min(match_score, 1.0)
    
    def _generate_prompt_from_template(self, template: PromptTemplate, context: Dict[str, Any], user_intent: str) -> str:
        """从模板生成prompt"""
        prompt = template.template
        
        # 替换变量
        for variable in template.variables:
            value = context.get(variable, f"{{{variable}}}")
            prompt = prompt.replace(f"{{{variable}}}", str(value))
        
        return prompt
    
    def _generate_default_prompt(self, category: str, context: Dict[str, Any], user_intent: str) -> str:
        """生成默认prompt"""
        if category == "meditation":
            return f"请深度分析以下用户意图：{user_intent}\n上下文：{context}"
        elif category == "orchestration":
            return f"请为以下意图制定工具协调计划：{user_intent}\n上下文：{context}"
        else:
            return f"请处理以下请求：{user_intent}\n上下文：{context}"
    
    async def get_learning_insights(self, pattern_type: str = None) -> List[LearningInsight]:
        """获取学习洞察"""
        if pattern_type:
            return [insight for insight in self.learning_insights if insight.pattern_type == pattern_type]
        return self.learning_insights
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 计算总体指标
        cursor.execute('SELECT COUNT(*) FROM interaction_records')
        total_interactions = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(CAST(human_feedback->"$.human_rating.rating" AS REAL)) FROM interaction_records WHERE human_feedback IS NOT NULL')
        avg_rating = cursor.fetchone()[0] or 0.0
        
        cursor.execute('SELECT COUNT(*) FROM interaction_records WHERE CAST(human_feedback->"$.human_rating.rating" AS REAL) >= 4.0')
        high_rating_count = cursor.fetchone()[0]
        
        success_rate = (high_rating_count / total_interactions * 100) if total_interactions > 0 else 0.0
        
        conn.close()
        
        return {
            "total_interactions": total_interactions,
            "average_rating": avg_rating,
            "success_rate": success_rate,
            "high_rating_count": high_rating_count,
            "learning_insights_count": len(self.learning_insights),
            "prompt_templates_count": len(self.prompt_templates)
        }

# 全局实例
training_module = TrainingModule()
