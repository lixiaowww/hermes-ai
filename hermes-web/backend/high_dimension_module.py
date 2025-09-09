"""
HighDimensionModule - 高维分析模块

基于V4.0设计，实现高维分析、突破思维定式和超越时空的智慧洞察。
从更高维度分析问题，突破思维定式，获得更高能的解决方案和认知。
"""

import os
import ast
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class DimensionalEntity:
    """高维实体"""
    name: str
    entity_type: str  # concept, pattern, principle, energy, consciousness
    dimension_level: int  # 维度层次：1-10
    transcendence_score: float  # 超越度：0-1
    wisdom_level: float  # 智慧层次：0-1
    energy_frequency: float  # 能量频率
    consciousness_level: str  # 意识层次：individual, collective, universal, transcendent
    universal_principles: List[str]  # 宇宙法则
    timeless_truths: List[str]  # 永恒真理

@dataclass
class DimensionalImpact:
    """高维影响分析"""
    entity: DimensionalEntity
    affected_dimensions: List[int]  # 影响的维度层次
    impact_scope: str  # local, dimensional, universal, transcendent
    transcendence_effect: float  # 超越效应
    wisdom_transmission: List[str]  # 智慧传递路径
    universal_resonance: float  # 宇宙共振度
    timeless_implications: List[str]  # 永恒影响

@dataclass
class TranscendencePattern:
    """超越模式分析"""
    entity: DimensionalEntity
    pattern_type: str  # breakthrough, transcendence, evolution, transformation
    pattern_description: str
    transcendence_path: List[str]  # 超越路径
    consciousness_shift: str  # 意识转变
    energy_transformation: str  # 能量转化
    wisdom_emergence: List[str]  # 智慧涌现

@dataclass
class ImpactReport:
    """影响报告"""
    analysis_id: str
    target_entity: str
    architecture_impacts: List[ArchitectureImpact]
    concurrency_risks: List[ConcurrencyRisk]
    overall_risk_score: float
    recommendations: List[str]
    timestamp: datetime

class HighDimensionModule:
    """
    高维模块 - 代码分析引擎
    
    功能：
    1. 宏观架构影响分析
    2. 微观并发风险分析
    3. 全面影响报告生成
    4. 代码依赖分析
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.code_entities: Dict[str, CodeEntity] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        
        # 风险模式定义 - 使用简单字符串匹配替代正则表达式
        self.risk_patterns = {
            "race_condition": [
                "threading.Thread",
                "multiprocessing.Process", 
                "asyncio.create_task",
                "concurrent.futures"
            ],
            "deadlock": [
                "lock.acquire",
                "with lock",
                "RLock",
                "Semaphore"
            ],
            "resource_contention": [
                "open(",
                "file(",
                "database",
                "connection",
                "pool"
            ]
        }
        
        # 复杂度计算权重
        self.complexity_weights = {
            "cyclomatic": 0.4,
            "nesting": 0.3,
            "lines": 0.2,
            "parameters": 0.1
        }
    
    async def analyze_codebase(self, target_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        分析代码库
        
        Args:
            target_paths: 目标路径列表（可选）
            
        Returns:
            Dict: 分析结果
        """
        logger.info("Starting codebase analysis...")
        
        # 扫描代码文件
        code_files = await self._scan_code_files(target_paths)
        
        # 解析代码实体
        entities = await self._parse_code_entities(code_files)
        
        # 构建依赖图
        await self._build_dependency_graph(entities)
        
        # 计算复杂度
        await self._calculate_complexity(entities)
        
        # 评估风险
        await self._assess_risks(entities)
        
        self.code_entities = {entity.name: entity for entity in entities}
        
        return {
            "total_entities": len(entities),
            "files_analyzed": len(code_files),
            "entities": [self._entity_to_dict(entity) for entity in entities],
            "dependency_graph": {k: list(v) for k, v in self.dependency_graph.items()},
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    async def _scan_code_files(self, target_paths: Optional[List[str]] = None) -> List[Path]:
        """扫描代码文件 - 优化版本"""
        code_files = []
        
        if target_paths:
            paths = [self.project_root / path for path in target_paths]
        else:
            # 限制默认扫描范围，避免扫描整个项目
            paths = [self.project_root / "main.py", self.project_root / "models.py"]
        
        # 排除的目录和文件
        exclude_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'}
        exclude_files = {'test_', '__init__.py'}
        
        for path in paths:
            if path.is_file() and path.suffix == '.py':
                # 检查是否应该排除
                if not any(exclude in path.name for exclude in exclude_files):
                    code_files.append(path)
            elif path.is_dir():
                # 限制递归深度和文件数量
                max_files = 50  # 最多处理50个文件
                file_count = 0
                
                for py_file in path.rglob('*.py'):
                    if file_count >= max_files:
                        break
                    
                    # 检查是否应该排除
                    if (not any(exclude in py_file.name for exclude in exclude_files) and
                        not any(exclude in str(py_file) for exclude in exclude_dirs)):
                        code_files.append(py_file)
                        file_count += 1
        
        logger.info(f"Found {len(code_files)} Python files (optimized scan)")
        return code_files
    
    async def _parse_code_entities(self, code_files: List[Path]) -> List[CodeEntity]:
        """解析代码实体 - 优化版本"""
        entities = []
        
        # 并行处理文件解析
        import asyncio
        
        async def parse_single_file(file_path: Path) -> List[CodeEntity]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 限制文件大小，跳过过大的文件
                if len(content) > 100000:  # 100KB限制
                    logger.warning(f"Skipping large file: {file_path}")
                    return []
                
                tree = ast.parse(content)
                file_entities = await self._extract_entities_from_ast(
                    tree, str(file_path.relative_to(self.project_root))
                )
                return file_entities
                
            except Exception as e:
                logger.warning(f"Failed to parse {file_path}: {e}")
                return []
        
        # 限制并发数量，避免内存问题
        semaphore = asyncio.Semaphore(5)
        
        async def parse_with_semaphore(file_path: Path):
            async with semaphore:
                return await parse_single_file(file_path)
        
        # 并行处理文件
        tasks = [parse_with_semaphore(file_path) for file_path in code_files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 收集结果
        for result in results:
            if isinstance(result, list):
                entities.extend(result)
            elif isinstance(result, Exception):
                logger.warning(f"Task failed: {result}")
        
        return entities
    
    async def _extract_entities_from_ast(self, tree: ast.AST, file_path: str) -> List[CodeEntity]:
        """从AST中提取实体 - 优化版本"""
        entities = []
        
        # 限制实体数量，避免处理过多实体
        max_entities_per_file = 20
        entity_count = 0
        
        for node in ast.walk(tree):
            if entity_count >= max_entities_per_file:
                break
                
            if isinstance(node, ast.FunctionDef):
                # 跳过私有函数和测试函数
                if node.name.startswith('_') and not node.name.startswith('__'):
                    continue
                if node.name.startswith('test_'):
                    continue
                    
                entity = CodeEntity(
                    name=node.name,
                    type="function",
                    file_path=file_path,
                    line_number=node.lineno,
                    dependencies=await self._extract_dependencies(node),
                    dependents=[],
                    complexity_score=0.0,
                    risk_level="low"
                )
                entities.append(entity)
                entity_count += 1
                
            elif isinstance(node, ast.ClassDef):
                # 跳过私有类
                if node.name.startswith('_') and not node.name.startswith('__'):
                    continue
                    
                entity = CodeEntity(
                    name=node.name,
                    type="class",
                    file_path=file_path,
                    line_number=node.lineno,
                    dependencies=await self._extract_dependencies(node),
                    dependents=[],
                    complexity_score=0.0,
                    risk_level="low"
                )
                entities.append(entity)
                entity_count += 1
        
        return entities
    
    async def _extract_dependencies(self, node: ast.AST) -> List[str]:
        """提取依赖关系 - 优化版本"""
        dependencies = []
        
        # 限制依赖提取的深度，避免过度递归
        max_depth = 3
        current_depth = 0
        
        def extract_from_node(n: ast.AST, depth: int = 0):
            nonlocal current_depth
            if depth > max_depth:
                return
                
            current_depth = depth
            
            if isinstance(n, ast.Import):
                for alias in n.names:
                    dependencies.append(alias.name)
            elif isinstance(n, ast.ImportFrom):
                if n.module:
                    dependencies.append(n.module)
            elif isinstance(n, ast.Call):
                if isinstance(n.func, ast.Name):
                    dependencies.append(n.func.id)
                elif isinstance(n.func, ast.Attribute):
                    # 只提取直接的模块名
                    if isinstance(n.func.value, ast.Name):
                        dependencies.append(n.func.value.id)
            
            # 只处理直接子节点，避免深度递归
            if depth < max_depth:
                for child in ast.iter_child_nodes(n):
                    extract_from_node(child, depth + 1)
        
        extract_from_node(node)
        
        # 去重并限制数量
        unique_deps = list(set(dependencies))
        return unique_deps[:10]  # 最多返回10个依赖
    
    async def _build_dependency_graph(self, entities: List[CodeEntity]):
        """构建依赖图"""
        self.dependency_graph = {}
        
        for entity in entities:
            self.dependency_graph[entity.name] = set()
            
            for dep in entity.dependencies:
                # 查找依赖的实体
                for other_entity in entities:
                    if dep in other_entity.name or other_entity.name in dep:
                        self.dependency_graph[entity.name].add(other_entity.name)
                        other_entity.dependents.append(entity.name)
    
    async def _calculate_complexity(self, entities: List[CodeEntity]):
        """计算复杂度"""
        for entity in entities:
            complexity = await self._calculate_entity_complexity(entity)
            entity.complexity_score = complexity
    
    async def _calculate_entity_complexity(self, entity: CodeEntity) -> float:
        """计算实体复杂度"""
        # 简化的复杂度计算
        base_complexity = 1.0
        
        # 基于依赖数量
        dep_complexity = len(entity.dependencies) * 0.1
        
        # 基于被依赖数量
        dependent_complexity = len(entity.dependents) * 0.05
        
        # 基于实体类型
        type_complexity = {
            "function": 0.5,
            "class": 1.0,
            "module": 0.2
        }.get(entity.type, 0.5)
        
        total_complexity = base_complexity + dep_complexity + dependent_complexity + type_complexity
        
        return min(total_complexity, 10.0)  # 限制最大复杂度
    
    async def _assess_risks(self, entities: List[CodeEntity]):
        """评估风险"""
        for entity in entities:
            risk_level = await self._assess_entity_risk(entity)
            entity.risk_level = risk_level
    
    async def _assess_entity_risk(self, entity: CodeEntity) -> str:
        """评估实体风险"""
        risk_score = 0
        
        # 基于复杂度
        if entity.complexity_score > 7:
            risk_score += 3
        elif entity.complexity_score > 4:
            risk_score += 2
        elif entity.complexity_score > 2:
            risk_score += 1
        
        # 基于依赖数量
        if len(entity.dependencies) > 10:
            risk_score += 2
        elif len(entity.dependencies) > 5:
            risk_score += 1
        
        # 基于被依赖数量
        if len(entity.dependents) > 5:
            risk_score += 2
        elif len(entity.dependents) > 2:
            risk_score += 1
        
        # 基于风险模式 - 使用简单字符串包含检查
        for risk_type, patterns in self.risk_patterns.items():
            for pattern in patterns:
                if pattern.lower() in entity.name.lower():
                    risk_score += 2
        
        if risk_score >= 6:
            return "critical"
        elif risk_score >= 4:
            return "high"
        elif risk_score >= 2:
            return "medium"
        else:
            return "low"
    
    async def analyze_architecture_impact(self, target_entity: str) -> List[ArchitectureImpact]:
        """分析架构影响"""
        if target_entity not in self.code_entities:
            raise ValueError(f"Entity {target_entity} not found")
        
        entity = self.code_entities[target_entity]
        impacts = []
        
        # 分析直接影响
        for dependent in entity.dependents:
            if dependent in self.code_entities:
                dependent_entity = self.code_entities[dependent]
                impact = ArchitectureImpact(
                    entity=dependent_entity,
                    affected_modules=[dependent_entity.file_path],
                    impact_scope=self._determine_impact_scope(dependent_entity),
                    risk_assessment=self._assess_impact_risk(entity, dependent_entity),
                    mitigation_suggestions=self._suggest_mitigations(entity, dependent_entity),
                    confidence_score=0.8
                )
                impacts.append(impact)
        
        # 分析间接影响
        indirect_impacts = await self._analyze_indirect_impacts(entity)
        impacts.extend(indirect_impacts)
        
        return impacts
    
    def _determine_impact_scope(self, entity: CodeEntity) -> str:
        """确定影响范围"""
        if len(entity.dependents) > 10:
            return "global"
        elif len(entity.dependents) > 5:
            return "system"
        elif len(entity.dependents) > 2:
            return "module"
        else:
            return "local"
    
    def _assess_impact_risk(self, source: CodeEntity, target: CodeEntity) -> str:
        """评估影响风险"""
        if source.risk_level == "critical" or target.risk_level == "critical":
            return "high"
        elif source.risk_level == "high" or target.risk_level == "high":
            return "medium"
        else:
            return "low"
    
    def _suggest_mitigations(self, source: CodeEntity, target: CodeEntity) -> List[str]:
        """建议缓解措施"""
        suggestions = []
        
        if source.risk_level == "critical":
            suggestions.append("Consider refactoring the source entity to reduce complexity")
        
        if target.risk_level == "critical":
            suggestions.append("Add error handling and validation in the target entity")
        
        if len(target.dependents) > 5:
            suggestions.append("Consider breaking down the target entity into smaller components")
        
        return suggestions
    
    async def _analyze_indirect_impacts(self, entity: CodeEntity) -> List[ArchitectureImpact]:
        """分析间接影响"""
        impacts = []
        visited = set()
        
        def analyze_recursive(current_entity: CodeEntity, depth: int = 0):
            if depth > 3 or current_entity.name in visited:
                return
            
            visited.add(current_entity.name)
            
            for dependent in current_entity.dependents:
                if dependent in self.code_entities:
                    dependent_entity = self.code_entities[dependent]
                    impact = ArchitectureImpact(
                        entity=dependent_entity,
                        affected_modules=[dependent_entity.file_path],
                        impact_scope="indirect",
                        risk_assessment="low",
                        mitigation_suggestions=["Monitor indirect dependencies"],
                        confidence_score=0.6 - (depth * 0.1)
                    )
                    impacts.append(impact)
                    analyze_recursive(dependent_entity, depth + 1)
        
        analyze_recursive(entity)
        return impacts
    
    async def analyze_concurrency_risks(self, target_entity: str) -> List[ConcurrencyRisk]:
        """分析并发风险"""
        if target_entity not in self.code_entities:
            raise ValueError(f"Entity {target_entity} not found")
        
        entity = self.code_entities[target_entity]
        risks = []
        
        # 检查并发模式 - 使用简单字符串包含检查
        for risk_type, patterns in self.risk_patterns.items():
            for pattern in patterns:
                if pattern.lower() in entity.name.lower():
                    risk = ConcurrencyRisk(
                        entity=entity,
                        risk_type=risk_type,
                        risk_description=f"Potential {risk_type} in {entity.name}",
                        affected_operations=[entity.name],
                        severity=self._assess_concurrency_severity(risk_type, entity),
                        mitigation_strategies=self._suggest_concurrency_mitigations(risk_type)
                    )
                    risks.append(risk)
        
        return risks
    
    def _assess_concurrency_severity(self, risk_type: str, entity: CodeEntity) -> str:
        """评估并发严重性"""
        if entity.risk_level == "critical":
            return "critical"
        elif risk_type == "deadlock":
            return "high"
        elif risk_type == "race_condition":
            return "medium"
        else:
            return "low"
    
    def _suggest_concurrency_mitigations(self, risk_type: str) -> List[str]:
        """建议并发缓解措施"""
        mitigations = {
            "race_condition": [
                "Use thread-safe data structures",
                "Implement proper locking mechanisms",
                "Consider using atomic operations"
            ],
            "deadlock": [
                "Implement lock ordering",
                "Use timeout mechanisms",
                "Avoid nested locking"
            ],
            "resource_contention": [
                "Implement connection pooling",
                "Use resource limits",
                "Consider caching strategies"
            ]
        }
        
        return mitigations.get(risk_type, ["Review and refactor code"])
    
    async def generate_impact_report(self, target_entity: str) -> ImpactReport:
        """生成影响报告"""
        analysis_id = f"impact_{target_entity}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 分析架构影响
        architecture_impacts = await self.analyze_architecture_impact(target_entity)
        
        # 分析并发风险
        concurrency_risks = await self.analyze_concurrency_risks(target_entity)
        
        # 计算总体风险分数
        overall_risk_score = self._calculate_overall_risk_score(
            architecture_impacts, concurrency_risks
        )
        
        # 生成建议
        recommendations = self._generate_recommendations(
            architecture_impacts, concurrency_risks
        )
        
        return ImpactReport(
            analysis_id=analysis_id,
            target_entity=target_entity,
            architecture_impacts=architecture_impacts,
            concurrency_risks=concurrency_risks,
            overall_risk_score=overall_risk_score,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    def _calculate_overall_risk_score(self, 
                                    architecture_impacts: List[ArchitectureImpact],
                                    concurrency_risks: List[ConcurrencyRisk]) -> float:
        """计算总体风险分数"""
        score = 0.0
        
        # 架构影响分数
        for impact in architecture_impacts:
            if impact.risk_assessment == "high":
                score += 0.3
            elif impact.risk_assessment == "medium":
                score += 0.2
            else:
                score += 0.1
        
        # 并发风险分数
        for risk in concurrency_risks:
            if risk.severity == "critical":
                score += 0.4
            elif risk.severity == "high":
                score += 0.3
            elif risk.severity == "medium":
                score += 0.2
            else:
                score += 0.1
        
        return min(score, 1.0)
    
    def _generate_recommendations(self,
                                architecture_impacts: List[ArchitectureImpact],
                                concurrency_risks: List[ConcurrencyRisk]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于架构影响的建议
        for impact in architecture_impacts:
            recommendations.extend(impact.mitigation_suggestions)
        
        # 基于并发风险的建议
        for risk in concurrency_risks:
            recommendations.extend(risk.mitigation_strategies)
        
        # 去重
        return list(set(recommendations))
    
    def _entity_to_dict(self, entity: CodeEntity) -> Dict[str, Any]:
        """将实体转换为字典"""
        return {
            "name": entity.name,
            "type": entity.type,
            "file_path": entity.file_path,
            "line_number": entity.line_number,
            "dependencies": entity.dependencies,
            "dependents": entity.dependents,
            "complexity_score": entity.complexity_score,
            "risk_level": entity.risk_level
        }

# 全局实例
high_dimension_module = HighDimensionModule()
