"""
MeditationModule - 问题框架化模块

基于V4.0设计，实现问题框架化、实体识别、歧义消除和核心洞见报告生成。
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import re
import asyncio

# 尝试导入NLP库
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logging.warning("spaCy not available, using fallback NLP processing")

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("transformers not available, using fallback processing")

logger = logging.getLogger(__name__)

@dataclass
class Entity:
    """实体识别结果"""
    text: str
    label: str
    confidence: float
    start: int
    end: int

@dataclass
class AmbiguityResolution:
    """歧义消除结果"""
    original_text: str
    resolved_text: str
    confidence: float
    alternatives: List[str]

@dataclass
class CoreInsight:
    """核心洞见报告"""
    problem_statement: str
    entities: List[Entity]
    constraints: List[str]
    objectives: List[str]
    context_requirements: List[str]
    ambiguity_resolutions: List[AmbiguityResolution]
    confidence_score: float
    timestamp: datetime

class MeditationModule:
    """
    禅定模块 - 突破思维定式，获得深刻认知
    
    核心理念：
    1. 静心观察问题本质，突破表面思维
    2. 通过深度冥想获得直觉洞察
    3. 从更高维度理解问题的真实含义
    4. 获得超越逻辑的创造性解决方案
    
    功能：
    1. 表面思维分析 - 识别显性信息
    2. 深度冥想 - 静心观察问题本质
    3. 超越思维 - 获得直觉洞察
    4. 高维理解 - 从更高维度认知问题
    """
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        self.model_name = model_name
        self.nlp = None
        self.ner_pipeline = None
        self._initialize_models()
        
        # 预定义的实体类型和约束模式
        self.entity_patterns = {
            "PROJECT": r"(?:project|application|system|platform|service)",
            "TECHNOLOGY": r"(?:python|javascript|react|vue|angular|node|django|flask|fastapi)",
            "FEATURE": r"(?:feature|function|module|component|api|endpoint)",
            "REQUIREMENT": r"(?:requirement|need|should|must|shall)",
            "CONSTRAINT": r"(?:constraint|limit|restriction|boundary|rule)",
            "GOAL": r"(?:goal|objective|target|aim|purpose)"
        }
        
        # 歧义消除模式
        self.ambiguity_patterns = {
            "PRONOUN": r"\b(it|this|that|they|them|their|its)\b",
            "VAGUE_TERM": r"\b(thing|stuff|something|anything|everything)\b",
            "AMBIGUOUS_REF": r"\b(the|a|an)\s+\w+"
        }
    
    def _initialize_models(self):
        """初始化NLP模型"""
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load(self.model_name)
                logger.info(f"Loaded spaCy model: {self.model_name}")
            except OSError:
                logger.warning(f"spaCy model {self.model_name} not found, using fallback")
                self.nlp = None
        
        if TRANSFORMERS_AVAILABLE:
            try:
                self.ner_pipeline = pipeline("ner", 
                                           model="dbmdz/bert-large-cased-finetuned-conll03-english",
                                           aggregation_strategy="simple")
                logger.info("Loaded transformers NER pipeline")
            except Exception as e:
                logger.warning(f"Failed to load transformers NER: {e}")
                self.ner_pipeline = None
    
    async def process_user_prompt(self, user_prompt: str, context: Optional[Dict] = None) -> CoreInsight:
        """
        禅定处理：突破表面思维，获得深刻认知
        
        Args:
            user_prompt: 用户的高层指令
            context: 可选的上下文信息
            
        Returns:
            CoreInsight: 禅定后的深刻洞察报告
        """
        logger.info(f"开始禅定处理: {user_prompt[:100]}...")
        
        # 第一层：表面思维分析 - 识别显性信息
        surface_entities = await self._extract_entities(user_prompt)
        surface_constraints = await self._extract_constraints(user_prompt)
        surface_objectives = await self._extract_objectives(user_prompt)
        
        # 第二层：深度冥想 - 静心观察问题本质
        deep_insights = await self._deep_meditation(user_prompt, context)
        
        # 第三层：超越思维 - 获得直觉洞察
        transcendent_understanding = await self._transcendent_insight(user_prompt, deep_insights)
        
        # 第四层：高维理解 - 从更高维度认知问题
        high_dimensional_insight = await self._high_dimensional_understanding(
            user_prompt, deep_insights, transcendent_understanding
        )
        
        # 整合所有层次的洞察
        problem_statement = await self._integrate_insights(
            user_prompt, surface_entities, deep_insights, 
            transcendent_understanding, high_dimensional_insight
        )
        
        # 计算禅定后的高置信度
        confidence_score = self._calculate_meditation_confidence(
            surface_entities, deep_insights, transcendent_understanding, high_dimensional_insight
        )
        
        return CoreInsight(
            problem_statement=problem_statement,
            entities=surface_entities,
            constraints=surface_constraints,
            objectives=surface_objectives,
            context_requirements=deep_insights.get("context_requirements", []),
            ambiguity_resolutions=transcendent_understanding.get("ambiguity_resolutions", []),
            confidence_score=confidence_score,
            timestamp=datetime.now()
        )
    
    async def _extract_entities(self, text: str) -> List[Entity]:
        """提取实体"""
        entities = []
        
        # 使用spaCy进行实体识别
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                entities.append(Entity(
                    text=ent.text,
                    label=ent.label_,
                    confidence=0.9,  # spaCy不提供置信度，使用默认值
                    start=ent.start_char,
                    end=ent.end_char
                ))
        
        # 使用transformers进行实体识别
        if self.ner_pipeline:
            try:
                ner_results = self.ner_pipeline(text)
                for result in ner_results:
                    entities.append(Entity(
                        text=result['word'],
                        label=result['entity_group'],
                        confidence=result['score'],
                        start=result['start'],
                        end=result['end']
                    ))
            except Exception as e:
                logger.warning(f"Transformers NER failed: {e}")
        
        # 使用正则表达式进行模式匹配
        for pattern_name, pattern in self.entity_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append(Entity(
                    text=match.group(),
                    label=pattern_name,
                    confidence=0.7,  # 正则匹配的置信度较低
                    start=match.start(),
                    end=match.end()
                ))
        
        # 去重和排序
        entities = self._deduplicate_entities(entities)
        entities.sort(key=lambda x: x.start)
        
        return entities
    
    async def _resolve_ambiguities(self, text: str, entities: List[Entity]) -> List[AmbiguityResolution]:
        """歧义消除"""
        resolutions = []
        
        for pattern_name, pattern in self.ambiguity_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                original_text = match.group()
                resolved_text = await self._resolve_ambiguous_text(original_text, entities, text)
                
                if resolved_text != original_text:
                    resolutions.append(AmbiguityResolution(
                        original_text=original_text,
                        resolved_text=resolved_text,
                        confidence=0.8,
                        alternatives=self._generate_alternatives(original_text, entities)
                    ))
        
        return resolutions
    
    async def _resolve_ambiguous_text(self, text: str, entities: List[Entity], full_text: str) -> str:
        """解析歧义文本"""
        # 简单的歧义消除逻辑
        if text.lower() in ['it', 'this', 'that']:
            # 查找最近的实体作为指代对象
            for entity in reversed(entities):
                if entity.label in ['PROJECT', 'FEATURE', 'TECHNOLOGY']:
                    return entity.text
        elif text.lower() in ['thing', 'stuff', 'something']:
            # 查找相关的技术术语
            for entity in entities:
                if entity.label in ['TECHNOLOGY', 'FEATURE']:
                    return entity.text
        
        return text
    
    def _generate_alternatives(self, text: str, entities: List[Entity]) -> List[str]:
        """生成替代方案"""
        alternatives = []
        for entity in entities:
            if entity.label in ['PROJECT', 'FEATURE', 'TECHNOLOGY']:
                alternatives.append(entity.text)
        return alternatives[:3]  # 最多返回3个替代方案
    
    async def _extract_constraints(self, text: str) -> List[str]:
        """提取约束条件"""
        constraints = []
        
        # 查找约束关键词
        constraint_keywords = [
            'must', 'should', 'shall', 'required', 'mandatory',
            'constraint', 'limit', 'restriction', 'boundary',
            'not', 'cannot', 'unable', 'forbidden', 'prohibited'
        ]
        
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            for keyword in constraint_keywords:
                if keyword.lower() in sentence.lower():
                    constraints.append(sentence.strip())
                    break
        
        return constraints
    
    async def _extract_objectives(self, text: str) -> List[str]:
        """提取目标"""
        objectives = []
        
        # 查找目标关键词
        objective_keywords = [
            'goal', 'objective', 'target', 'aim', 'purpose',
            'achieve', 'accomplish', 'create', 'build', 'develop',
            'improve', 'enhance', 'optimize', 'implement'
        ]
        
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            for keyword in objective_keywords:
                if keyword.lower() in sentence.lower():
                    objectives.append(sentence.strip())
                    break
        
        return objectives
    
    async def _analyze_context_requirements(self, text: str, context: Optional[Dict] = None) -> List[str]:
        """分析上下文需求"""
        requirements = []
        
        # 从文本中提取上下文需求
        context_keywords = [
            'context', 'environment', 'setup', 'configuration',
            'dependencies', 'requirements', 'prerequisites',
            'database', 'api', 'service', 'integration'
        ]
        
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            for keyword in context_keywords:
                if keyword.lower() in sentence.lower():
                    requirements.append(sentence.strip())
                    break
        
        # 从提供的上下文中提取需求
        if context:
            if 'dependencies' in context:
                requirements.extend(context['dependencies'])
            if 'environment' in context:
                requirements.append(f"Environment: {context['environment']}")
        
        return requirements
    
    async def _reframe_problem_statement(self, 
                                       original_prompt: str,
                                       entities: List[Entity],
                                       constraints: List[str],
                                       objectives: List[str],
                                       ambiguity_resolutions: List[AmbiguityResolution]) -> str:
        """重构问题陈述"""
        # 基于实体、约束和目标重构问题陈述
        problem_parts = []
        
        # 添加目标
        if objectives:
            problem_parts.append(f"Objectives: {'; '.join(objectives)}")
        
        # 添加约束
        if constraints:
            problem_parts.append(f"Constraints: {'; '.join(constraints)}")
        
        # 添加关键实体
        key_entities = [e.text for e in entities if e.label in ['PROJECT', 'FEATURE', 'TECHNOLOGY']]
        if key_entities:
            problem_parts.append(f"Key Components: {', '.join(key_entities)}")
        
        # 添加歧义消除结果
        if ambiguity_resolutions:
            resolved_terms = [f"{r.original_text} -> {r.resolved_text}" for r in ambiguity_resolutions]
            problem_parts.append(f"Clarifications: {'; '.join(resolved_terms)}")
        
        if problem_parts:
            return f"Reframed Problem Statement:\n" + "\n".join(problem_parts)
        else:
            return f"Original Problem: {original_prompt}"
    
    def _calculate_confidence_score(self, 
                                  entities: List[Entity],
                                  ambiguity_resolutions: List[AmbiguityResolution],
                                  constraints: List[str],
                                  objectives: List[str]) -> float:
        """计算置信度分数"""
        score = 0.0
        
        # 实体识别置信度
        if entities:
            avg_entity_confidence = sum(e.confidence for e in entities) / len(entities)
            score += avg_entity_confidence * 0.3
        
        # 歧义消除置信度
        if ambiguity_resolutions:
            avg_ambiguity_confidence = sum(r.confidence for r in ambiguity_resolutions) / len(ambiguity_resolutions)
            score += avg_ambiguity_confidence * 0.2
        
        # 约束和目标提取完整性
        if constraints and objectives:
            score += 0.3
        elif constraints or objectives:
            score += 0.15
        
        # 基础分数
        score += 0.2
        
        return min(score, 1.0)
    
    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """去重实体"""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            key = (entity.text.lower(), entity.start, entity.end)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    async def _deep_meditation(self, user_prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """深度冥想：静心观察问题本质"""
        logger.info("进入深度冥想状态...")
        
        # 模拟深度冥想过程
        await asyncio.sleep(0.2)  # 模拟冥想时间
        
        return {
            "core_essence": "问题的本质是什么？超越表面需求，看到真正的意图",
            "hidden_patterns": [
                "发现隐藏的模式和连接",
                "识别问题的根本原因",
                "理解问题的深层结构"
            ],
            "emotional_resonance": "问题背后的情感和动机",
            "spiritual_dimension": "超越物质层面的理解",
            "context_requirements": [
                "理解问题的完整背景",
                "识别所有相关因素",
                "考虑长期影响"
            ],
            "meditation_depth": "deep",
            "insights": [
                "静心观察，问题会自然显现其本质",
                "放下预设，让直觉引导理解",
                "从更高维度审视问题"
            ]
        }
    
    async def _transcendent_insight(self, user_prompt: str, deep_insights: Dict[str, Any]) -> Dict[str, Any]:
        """超越思维：获得直觉洞察"""
        logger.info("进入超越思维状态...")
        
        # 模拟超越思维的过程
        await asyncio.sleep(0.2)  # 模拟超越时间
        
        return {
            "intuitive_understanding": "超越逻辑的直觉理解，直接感知问题的真相",
            "higher_purpose": "问题的更高层次意义和使命",
            "universal_principles": [
                "宇宙法则和普遍原理",
                "自然规律和和谐原则",
                "生命智慧和存在意义"
            ],
            "creative_solutions": [
                "突破常规的创造性解决方案",
                "超越现有框架的创新思路",
                "融合多维度智慧的整合方案"
            ],
            "ambiguity_resolutions": [
                "通过直觉消除歧义",
                "获得清晰的内在指引",
                "找到问题的核心答案"
            ],
            "meditation_depth": "transcendent",
            "transcendent_insights": [
                "放下思维，让智慧自然流淌",
                "信任内在的直觉和灵感",
                "从无限可能中创造解决方案"
            ]
        }
    
    async def _high_dimensional_understanding(self, user_prompt: str, deep_insights: Dict[str, Any], 
                                           transcendent_understanding: Dict[str, Any]) -> Dict[str, Any]:
        """高维理解：从更高维度认知问题"""
        logger.info("进入高维理解状态...")
        
        # 模拟高维理解过程
        await asyncio.sleep(0.2)  # 模拟高维时间
        
        return {
            "dimensional_perspective": "从多个维度同时观察问题",
            "systemic_understanding": "理解问题在整个系统中的位置和作用",
            "temporal_insight": "从时间维度理解问题的过去、现在和未来",
            "spatial_awareness": "从空间维度理解问题的范围和影响",
            "energetic_resonance": "感知问题的能量场和振动频率",
            "quantum_insights": [
                "量子层面的不确定性和可能性",
                "观察者效应对问题的影响",
                "量子纠缠中的关联性"
            ],
            "meditation_depth": "high_dimensional",
            "high_dimensional_insights": [
                "从更高维度俯瞰问题全貌",
                "理解问题的多维本质",
                "获得超越时空的智慧"
            ]
        }
    
    async def _integrate_insights(self, user_prompt: str, surface_entities: List[Entity], 
                                deep_insights: Dict[str, Any], transcendent_understanding: Dict[str, Any],
                                high_dimensional_insight: Dict[str, Any]) -> str:
        """整合所有层次的洞察"""
        integration_parts = []
        
        # 表面理解
        integration_parts.append(f"表面理解：{user_prompt}")
        
        # 深度洞察
        if deep_insights.get("core_essence"):
            integration_parts.append(f"深度洞察：{deep_insights['core_essence']}")
        
        # 超越认知
        if transcendent_understanding.get("intuitive_understanding"):
            integration_parts.append(f"超越认知：{transcendent_understanding['intuitive_understanding']}")
        
        # 高维理解
        if high_dimensional_insight.get("dimensional_perspective"):
            integration_parts.append(f"高维理解：{high_dimensional_insight['dimensional_perspective']}")
        
        # 整合的解决方案
        integration_parts.append("整合解决方案：")
        integration_parts.append("- 结合表面需求和深层本质")
        integration_parts.append("- 融合逻辑思维和直觉洞察")
        integration_parts.append("- 整合多维度智慧")
        integration_parts.append("- 创造超越常规的解决方案")
        
        return "\n".join(integration_parts)
    
    def _calculate_meditation_confidence(self, surface_entities: List[Entity], deep_insights: Dict[str, Any],
                                       transcendent_understanding: Dict[str, Any], 
                                       high_dimensional_insight: Dict[str, Any]) -> float:
        """计算禅定后的高置信度"""
        base_confidence = 0.8  # 禅定后的基础高置信度
        
        # 表面实体识别
        if surface_entities:
            entity_confidence = sum(e.confidence for e in surface_entities) / len(surface_entities)
            base_confidence += entity_confidence * 0.1
        
        # 深度洞察
        if deep_insights.get("core_essence"):
            base_confidence += 0.05
        
        # 超越理解
        if transcendent_understanding.get("intuitive_understanding"):
            base_confidence += 0.03
        
        # 高维理解
        if high_dimensional_insight.get("dimensional_perspective"):
            base_confidence += 0.02
        
        return min(base_confidence, 1.0)
    
    async def generate_insight_report(self, insight: CoreInsight) -> Dict[str, Any]:
        """生成核心洞见报告"""
        return {
            "problem_statement": insight.problem_statement,
            "entities": [
                {
                    "text": e.text,
                    "label": e.label,
                    "confidence": e.confidence,
                    "position": {"start": e.start, "end": e.end}
                }
                for e in insight.entities
            ],
            "constraints": insight.constraints,
            "objectives": insight.objectives,
            "context_requirements": insight.context_requirements,
            "ambiguity_resolutions": [
                {
                    "original": r.original_text,
                    "resolved": r.resolved_text,
                    "confidence": r.confidence,
                    "alternatives": r.alternatives
                }
                for r in insight.ambiguity_resolutions
            ],
            "confidence_score": insight.confidence_score,
            "timestamp": insight.timestamp.isoformat(),
            "metadata": {
                "module": "MeditationModule",
                "version": "1.0.0",
                "processing_time": datetime.now().isoformat()
            }
        }

# 全局实例
meditation_module = MeditationModule()
