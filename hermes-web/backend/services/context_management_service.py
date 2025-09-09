"""
Context Management Service
上下文管理服务 - 负责上下文的压缩、总结和防止腐烂
"""

import uuid
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)

class ContextType(Enum):
    """上下文类型枚举"""
    CONVERSATION = "conversation"
    CODE_ANALYSIS = "code_analysis"
    DEBATE_SESSION = "debate_session"
    MEDITATION_INSIGHT = "meditation_insight"
    TRAINING_DATA = "training_data"
    USER_FEEDBACK = "user_feedback"

class ContextPriority(Enum):
    """上下文优先级枚举"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ContextChunk:
    """上下文块数据结构"""
    id: str
    content: str
    context_type: ContextType
    priority: ContextPriority
    created_at: datetime
    last_accessed: datetime
    access_count: int
    importance_score: float
    compressed: bool = False
    summary: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class ContextSummary:
    """上下文总结数据结构"""
    id: str
    original_chunks: List[str]
    summary_text: str
    key_points: List[str]
    entities: List[str]
    relationships: List[Dict[str, str]]
    created_at: datetime
    quality_score: float

class ContextManagementService:
    """上下文管理服务"""
    
    def __init__(self):
        self.context_chunks: Dict[str, ContextChunk] = {}
        self.context_summaries: Dict[str, ContextSummary] = {}
        self.decay_threshold = 30  # 天
        self.compression_threshold = 100  # 字符数
        self.max_context_size = 10000  # 最大上下文大小
        
    async def store_context(
        self, 
        content: str, 
        context_type: ContextType,
        priority: ContextPriority = ContextPriority.MEDIUM,
        metadata: Dict[str, Any] = None
    ) -> str:
        """存储上下文"""
        try:
            context_id = str(uuid.uuid4())
            now = datetime.now()
            
            # 计算重要性分数
            importance_score = await self._calculate_importance_score(
                content, context_type, priority
            )
            
            # 创建上下文块
            chunk = ContextChunk(
                id=context_id,
                content=content,
                context_type=context_type,
                priority=priority,
                created_at=now,
                last_accessed=now,
                access_count=1,
                importance_score=importance_score,
                metadata=metadata or {}
            )
            
            self.context_chunks[context_id] = chunk
            
            logger.info(f"Stored context chunk: {context_id}")
            return context_id
            
        except Exception as e:
            logger.error(f"Error storing context: {str(e)}")
            raise
    
    async def retrieve_context(
        self, 
        query: str, 
        context_type: Optional[ContextType] = None,
        limit: int = 10
    ) -> List[ContextChunk]:
        """检索相关上下文"""
        try:
            # 计算查询的相关性分数
            relevant_chunks = []
            
            for chunk in self.context_chunks.values():
                if context_type and chunk.context_type != context_type:
                    continue
                
                # 计算相关性分数
                relevance_score = await self._calculate_relevance_score(
                    query, chunk.content
                )
                
                if relevance_score > 0.3:  # 相关性阈值
                    relevant_chunks.append((chunk, relevance_score))
            
            # 按相关性分数排序
            relevant_chunks.sort(key=lambda x: x[1], reverse=True)
            
            # 更新访问信息
            for chunk, _ in relevant_chunks[:limit]:
                chunk.last_accessed = datetime.now()
                chunk.access_count += 1
            
            return [chunk for chunk, _ in relevant_chunks[:limit]]
            
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            raise
    
    async def compress_context(self, context_id: str) -> bool:
        """压缩上下文"""
        try:
            if context_id not in self.context_chunks:
                return False
            
            chunk = self.context_chunks[context_id]
            
            if chunk.compressed or len(chunk.content) < self.compression_threshold:
                return False
            
            # 生成总结
            summary = await self._generate_summary(chunk.content)
            
            # 压缩内容
            compressed_content = await self._compress_content(chunk.content)
            
            # 更新上下文块
            chunk.content = compressed_content
            chunk.compressed = True
            chunk.summary = summary
            
            logger.info(f"Compressed context chunk: {context_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error compressing context: {str(e)}")
            return False
    
    async def summarize_contexts(
        self, 
        context_ids: List[str],
        summary_type: str = "general"
    ) -> str:
        """总结多个上下文"""
        try:
            chunks = []
            for context_id in context_ids:
                if context_id in self.context_chunks:
                    chunks.append(self.context_chunks[context_id])
            
            if not chunks:
                return ""
            
            # 合并内容
            combined_content = "\n\n".join([
                f"[{chunk.context_type.value}] {chunk.content}"
                for chunk in chunks
            ])
            
            # 生成总结
            summary = await self._generate_summary(combined_content)
            
            # 创建总结记录
            summary_id = str(uuid.uuid4())
            context_summary = ContextSummary(
                id=summary_id,
                original_chunks=context_ids,
                summary_text=summary,
                key_points=await self._extract_key_points(combined_content),
                entities=await self._extract_entities(combined_content),
                relationships=await self._extract_relationships(combined_content),
                created_at=datetime.now(),
                quality_score=await self._calculate_summary_quality(summary)
            )
            
            self.context_summaries[summary_id] = context_summary
            
            logger.info(f"Created context summary: {summary_id}")
            return summary_id
            
        except Exception as e:
            logger.error(f"Error summarizing contexts: {str(e)}")
            raise
    
    async def prevent_decay(self) -> int:
        """防止上下文腐烂"""
        try:
            decayed_count = 0
            now = datetime.now()
            decay_threshold = timedelta(days=self.decay_threshold)
            
            for context_id, chunk in list(self.context_chunks.items()):
                # 检查是否腐烂
                if now - chunk.last_accessed > decay_threshold:
                    # 根据重要性决定是否保留
                    if chunk.importance_score < 0.5:
                        # 低重要性，直接删除
                        del self.context_chunks[context_id]
                        decayed_count += 1
                        logger.info(f"Removed decayed context: {context_id}")
                    else:
                        # 高重要性，压缩保存
                        await self.compress_context(context_id)
                        decayed_count += 1
                        logger.info(f"Compressed decayed context: {context_id}")
            
            return decayed_count
            
        except Exception as e:
            logger.error(f"Error preventing decay: {str(e)}")
            raise
    
    async def get_context_statistics(self) -> Dict[str, Any]:
        """获取上下文统计信息"""
        try:
            total_chunks = len(self.context_chunks)
            compressed_chunks = sum(1 for chunk in self.context_chunks.values() if chunk.compressed)
            total_summaries = len(self.context_summaries)
            
            # 按类型统计
            type_counts = {}
            for chunk in self.context_chunks.values():
                type_name = chunk.context_type.value
                type_counts[type_name] = type_counts.get(type_name, 0) + 1
            
            # 按优先级统计
            priority_counts = {}
            for chunk in self.context_chunks.values():
                priority_name = chunk.priority.value
                priority_counts[priority_name] = priority_counts.get(priority_name, 0) + 1
            
            return {
                "total_chunks": total_chunks,
                "compressed_chunks": compressed_chunks,
                "total_summaries": total_summaries,
                "type_distribution": type_counts,
                "priority_distribution": priority_counts,
                "compression_rate": compressed_chunks / total_chunks if total_chunks > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            raise
    
    async def _calculate_importance_score(
        self, 
        content: str, 
        context_type: ContextType,
        priority: ContextPriority
    ) -> float:
        """计算重要性分数"""
        try:
            base_score = priority.value / 4.0  # 基于优先级的基础分数
            
            # 基于内容长度的分数
            length_score = min(len(content) / 1000, 1.0)
            
            # 基于上下文类型的分数
            type_scores = {
                ContextType.CONVERSATION: 0.8,
                ContextType.CODE_ANALYSIS: 0.9,
                ContextType.DEBATE_SESSION: 0.95,
                ContextType.MEDITATION_INSIGHT: 1.0,
                ContextType.TRAINING_DATA: 0.9,
                ContextType.USER_FEEDBACK: 0.85
            }
            type_score = type_scores.get(context_type, 0.5)
            
            # 综合分数
            importance_score = (base_score * 0.4 + length_score * 0.3 + type_score * 0.3)
            
            return min(importance_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating importance score: {str(e)}")
            return 0.5
    
    async def _calculate_relevance_score(self, query: str, content: str) -> float:
        """计算相关性分数"""
        try:
            # 简单的关键词匹配
            query_words = set(query.lower().split())
            content_words = set(content.lower().split())
            
            if not query_words:
                return 0.0
            
            # 计算交集比例
            intersection = query_words.intersection(content_words)
            relevance_score = len(intersection) / len(query_words)
            
            return relevance_score
            
        except Exception as e:
            logger.error(f"Error calculating relevance score: {str(e)}")
            return 0.0
    
    async def _generate_summary(self, content: str) -> str:
        """生成内容总结"""
        try:
            # 简单的总结逻辑 - 在实际应用中可以使用更复杂的NLP模型
            sentences = content.split('.')
            if len(sentences) <= 3:
                return content
            
            # 选择前3个句子作为总结
            summary = '. '.join(sentences[:3]) + '.'
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return content[:200] + "..." if len(content) > 200 else content
    
    async def _compress_content(self, content: str) -> str:
        """压缩内容"""
        try:
            # 简单的压缩逻辑 - 保留关键信息
            if len(content) <= self.compression_threshold:
                return content
            
            # 保留前200个字符和后200个字符
            if len(content) > 400:
                compressed = content[:200] + "\n... [compressed] ...\n" + content[-200:]
            else:
                compressed = content[:200] + "... [compressed]"
            
            return compressed
            
        except Exception as e:
            logger.error(f"Error compressing content: {str(e)}")
            return content
    
    async def _extract_key_points(self, content: str) -> List[str]:
        """提取关键点"""
        try:
            # 简单的关键点提取 - 在实际应用中可以使用更复杂的NLP模型
            sentences = content.split('.')
            key_points = []
            
            for sentence in sentences:
                if len(sentence.strip()) > 20:  # 过滤短句
                    key_points.append(sentence.strip())
                    if len(key_points) >= 5:  # 最多5个关键点
                        break
            
            return key_points
            
        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            return []
    
    async def _extract_entities(self, content: str) -> List[str]:
        """提取实体"""
        try:
            # 简单的实体提取 - 在实际应用中可以使用NER模型
            words = content.split()
            entities = []
            
            # 提取大写字母开头的词作为实体
            for word in words:
                if word[0].isupper() and len(word) > 2:
                    entities.append(word)
            
            return list(set(entities))  # 去重
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return []
    
    async def _extract_relationships(self, content: str) -> List[Dict[str, str]]:
        """提取关系"""
        try:
            # 简单的关系提取 - 在实际应用中可以使用更复杂的关系抽取模型
            relationships = []
            
            # 查找常见的关系模式
            if "caused by" in content.lower():
                relationships.append({"type": "causation", "description": "caused by"})
            if "related to" in content.lower():
                relationships.append({"type": "relation", "description": "related to"})
            if "depends on" in content.lower():
                relationships.append({"type": "dependency", "description": "depends on"})
            
            return relationships
            
        except Exception as e:
            logger.error(f"Error extracting relationships: {str(e)}")
            return []
    
    async def _calculate_summary_quality(self, summary: str) -> float:
        """计算总结质量分数"""
        try:
            # 基于总结长度的质量分数
            length_score = min(len(summary) / 500, 1.0)
            
            # 基于句子数量的质量分数
            sentence_count = len(summary.split('.'))
            sentence_score = min(sentence_count / 5, 1.0)
            
            # 综合质量分数
            quality_score = (length_score * 0.6 + sentence_score * 0.4)
            
            return min(quality_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating summary quality: {str(e)}")
            return 0.5

# 创建全局实例
context_management_service = ContextManagementService()
