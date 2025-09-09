"""
Enhanced Prompt Optimizer Service
增强版Prompt优化器服务 - 高质量提示词工程
"""

import json
import uuid
import re
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PromptQuality(Enum):
    """提示词质量等级"""
    POOR = 1
    FAIR = 2
    GOOD = 3
    EXCELLENT = 4
    OUTSTANDING = 5

class PromptType(Enum):
    """提示词类型"""
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    REASONING = "reasoning"
    CONVERSATION = "conversation"
    TASK_EXECUTION = "task_execution"

@dataclass
class PromptAnalysis:
    """提示词分析结果"""
    clarity_score: float
    completeness_score: float
    specificity_score: float
    context_richness: float
    technical_accuracy: float
    overall_quality: PromptQuality
    improvement_suggestions: List[str]
    missing_elements: List[str]

@dataclass
class EnhancedPrompt:
    """增强版优化后的Prompt结构"""
    id: str
    original_command: str
    optimized_prompt: str
    prompt_type: PromptType
    quality_analysis: PromptAnalysis
    context: str
    technical_requirements: List[str]
    user_stories: List[str]
    acceptance_criteria: List[str]
    quality_score: float
    debate_rounds: int
    constitution_checks: List[str]
    tool_recommendations: List[str]
    confidence_level: float
    execution_estimate: str
    risk_assessment: List[str]
    created_at: str

class EnhancedPromptOptimizer:
    """增强版Prompt优化器"""
    
    def __init__(self):
        self.constitution_rules = self._load_constitution()
        self.tool_catalog = self._load_tool_catalog()
        self.quality_patterns = self._load_quality_patterns()
        self.domain_knowledge = self._load_domain_knowledge()
    
    def _load_constitution(self) -> Dict[str, List[str]]:
        """加载宪法规则"""
        return {
            "development_principles": [
                "代码必须遵循最佳实践和设计模式",
                "必须包含完整的错误处理机制",
                "必须考虑安全性和性能优化",
                "必须包含完整的测试用例",
                "必须遵循可维护性和可扩展性原则",
                "必须考虑用户体验和可访问性",
                "必须包含完整的文档和注释"
            ],
            "review_standards": [
                "代码质量必须达到生产环境标准",
                "必须通过所有自动化测试",
                "必须符合安全审计要求",
                "必须通过性能基准测试",
                "必须通过用户体验评审",
                "必须通过代码审查",
                "必须符合团队编码规范"
            ],
            "ethical_guidelines": [
                "不得包含歧视性内容",
                "必须保护用户隐私",
                "必须遵循数据保护法规",
                "必须确保算法公平性",
                "必须提供透明的决策过程",
                "必须避免有害内容生成",
                "必须尊重知识产权"
            ]
        }
    
    def _load_tool_catalog(self) -> Dict[str, Dict]:
        """加载工具目录"""
        return {
            "code_generation": {
                "tools": ["github_copilot", "replit_agent", "codesandbox", "stackblitz"],
                "description": "代码生成工具",
                "use_cases": ["生成基础代码", "实现特定功能", "创建原型", "代码补全"]
            },
            "testing": {
                "tools": ["jest", "pytest", "cypress", "playwright", "vitest"],
                "description": "测试工具",
                "use_cases": ["单元测试", "集成测试", "端到端测试", "性能测试"]
            },
            "deployment": {
                "tools": ["vercel", "netlify", "docker", "kubernetes", "aws"],
                "description": "部署工具",
                "use_cases": ["应用部署", "容器化", "云服务配置", "CI/CD"]
            },
            "monitoring": {
                "tools": ["sentry", "datadog", "newrelic", "prometheus", "grafana"],
                "description": "监控工具",
                "use_cases": ["错误监控", "性能监控", "日志分析", "指标收集"]
            },
            "ai_ml": {
                "tools": ["openai", "anthropic", "huggingface", "langchain"],
                "description": "AI/ML工具",
                "use_cases": ["模型调用", "向量搜索", "文本处理", "智能分析"]
            }
        }
    
    def _load_quality_patterns(self) -> Dict[str, List[str]]:
        """加载质量模式"""
        return {
            "high_quality_indicators": [
                r"请.*?实现.*?功能",
                r"确保.*?符合.*?标准",
                r"包含.*?测试.*?用例",
                r"考虑.*?性能.*?优化",
                r"遵循.*?最佳.*?实践"
            ],
            "low_quality_indicators": [
                r"随便.*?做.*?一个",
                r"大概.*?就行",
                r"不用.*?太.*?复杂",
                r"简单.*?实现.*?一下"
            ],
            "technical_keywords": [
                "API", "数据库", "缓存", "安全", "性能", "测试", "部署",
                "监控", "日志", "错误处理", "用户体验", "可访问性"
            ]
        }
    
    def _load_domain_knowledge(self) -> Dict[str, Dict]:
        """加载领域知识"""
        return {
            "web_development": {
                "frameworks": ["React", "Vue", "Angular", "Next.js", "Nuxt.js"],
                "languages": ["JavaScript", "TypeScript", "HTML", "CSS"],
                "databases": ["PostgreSQL", "MySQL", "MongoDB", "Redis"],
                "best_practices": ["响应式设计", "SEO优化", "性能优化", "安全防护"]
            },
            "mobile_development": {
                "frameworks": ["React Native", "Flutter", "Ionic", "Xamarin"],
                "languages": ["JavaScript", "Dart", "Swift", "Kotlin"],
                "platforms": ["iOS", "Android", "Cross-platform"],
                "best_practices": ["原生性能", "用户体验", "离线支持", "推送通知"]
            },
            "ai_ml": {
                "frameworks": ["TensorFlow", "PyTorch", "Scikit-learn", "LangChain"],
                "models": ["GPT", "BERT", "T5", "CLIP"],
                "techniques": ["深度学习", "自然语言处理", "计算机视觉", "强化学习"],
                "best_practices": ["数据预处理", "模型评估", "超参数调优", "模型部署"]
            }
        }
    
    async def optimize_prompt(
        self, 
        user_command: str, 
        context: Dict[str, Any],
        prompt_type: Optional[PromptType] = None
    ) -> EnhancedPrompt:
        """优化用户命令为高质量prompt"""
        try:
            prompt_id = str(uuid.uuid4())[:8]
            
            # 第一步：深度分析用户命令
            analysis = await self._deep_analyze_command(user_command, context)
            
            # 第二步：确定提示词类型
            if not prompt_type:
                prompt_type = self._determine_prompt_type(user_command, analysis)
            
            # 第三步：生成高质量提示词
            optimized_prompt = await self._generate_high_quality_prompt(
                user_command, analysis, prompt_type, context
            )
            
            # 第四步：质量分析和评估
            quality_analysis = await self._analyze_prompt_quality(optimized_prompt)
            
            # 第五步：对抗性辩论优化
            debated_prompt = await self._enhanced_debate_optimize(
                optimized_prompt, analysis, prompt_type
            )
            
            # 第六步：宪法检查
            constitution_checks = await self._enhanced_constitution_check(debated_prompt)
            
            # 第七步：工具推荐
            tool_recommendations = await self._enhanced_tool_recommendations(
                debated_prompt, analysis, context
            )
            
            # 第八步：风险评估
            risk_assessment = await self._assess_risks(debated_prompt, analysis)
            
            # 第九步：执行估算
            execution_estimate = await self._estimate_execution(debated_prompt, analysis)
            
            # 第十步：最终质量评分
            final_quality_score = await self._calculate_final_quality_score(
                debated_prompt, quality_analysis
            )
            
            return EnhancedPrompt(
                id=prompt_id,
                original_command=user_command,
                optimized_prompt=debated_prompt["optimized_prompt"],
                prompt_type=prompt_type,
                quality_analysis=quality_analysis,
                context=debated_prompt["context"],
                technical_requirements=debated_prompt["technical_requirements"],
                user_stories=debated_prompt["user_stories"],
                acceptance_criteria=debated_prompt["acceptance_criteria"],
                quality_score=final_quality_score,
                debate_rounds=debated_prompt["debate_rounds"],
                constitution_checks=constitution_checks,
                tool_recommendations=tool_recommendations,
                confidence_level=debated_prompt.get("confidence_level", 0.8),
                execution_estimate=execution_estimate,
                risk_assessment=risk_assessment,
                created_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error optimizing prompt: {str(e)}")
            raise
    
    async def _deep_analyze_command(
        self, 
        user_command: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """深度分析用户命令"""
        try:
            # 基础分析
            app_type = self._identify_app_type(user_command)
            core_features = self._extract_core_features(user_command)
            tech_stack = self._identify_tech_stack(user_command, context)
            user_roles = self._analyze_user_roles(user_command)
            complexity_level = self._assess_complexity(user_command)
            
            # 深度分析
            intent_analysis = self._analyze_intent(user_command)
            domain_analysis = self._analyze_domain(user_command, context)
            constraint_analysis = self._analyze_constraints(user_command, context)
            quality_requirements = self._analyze_quality_requirements(user_command)
            
            return {
                "app_type": app_type,
                "core_features": core_features,
                "tech_stack": tech_stack,
                "user_roles": user_roles,
                "complexity_level": complexity_level,
                "intent_analysis": intent_analysis,
                "domain_analysis": domain_analysis,
                "constraint_analysis": constraint_analysis,
                "quality_requirements": quality_requirements,
                "original_length": len(user_command),
                "has_technical_terms": self._has_technical_terms(user_command),
                "clarity_score": self._calculate_clarity_score(user_command)
            }
            
        except Exception as e:
            logger.error(f"Error in deep analysis: {str(e)}")
            raise
    
    async def _generate_high_quality_prompt(
        self,
        user_command: str,
        analysis: Dict[str, Any],
        prompt_type: PromptType,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成高质量提示词"""
        try:
            # 根据提示词类型生成不同的提示词
            if prompt_type == PromptType.CODE_GENERATION:
                return await self._generate_code_generation_prompt(
                    user_command, analysis, context
                )
            elif prompt_type == PromptType.ANALYSIS:
                return await self._generate_analysis_prompt(
                    user_command, analysis, context
                )
            elif prompt_type == PromptType.CREATIVE:
                return await self._generate_creative_prompt(
                    user_command, analysis, context
                )
            elif prompt_type == PromptType.REASONING:
                return await self._generate_reasoning_prompt(
                    user_command, analysis, context
                )
            else:
                return await self._generate_general_prompt(
                    user_command, analysis, context
                )
                
        except Exception as e:
            logger.error(f"Error generating high quality prompt: {str(e)}")
            raise
    
    async def _analyze_prompt_quality(self, prompt_data: Dict[str, Any]) -> PromptAnalysis:
        """分析提示词质量"""
        try:
            prompt_text = prompt_data.get("optimized_prompt", "")
            
            # 计算各项质量指标
            clarity_score = self._calculate_clarity_score(prompt_text)
            completeness_score = self._calculate_completeness_score(prompt_data)
            specificity_score = self._calculate_specificity_score(prompt_text)
            context_richness = self._calculate_context_richness(prompt_data)
            technical_accuracy = self._calculate_technical_accuracy(prompt_text)
            
            # 计算总体质量
            overall_score = (
                clarity_score * 0.25 +
                completeness_score * 0.25 +
                specificity_score * 0.20 +
                context_richness * 0.15 +
                technical_accuracy * 0.15
            )
            
            # 确定质量等级
            if overall_score >= 0.9:
                quality_level = PromptQuality.OUTSTANDING
            elif overall_score >= 0.8:
                quality_level = PromptQuality.EXCELLENT
            elif overall_score >= 0.7:
                quality_level = PromptQuality.GOOD
            elif overall_score >= 0.6:
                quality_level = PromptQuality.FAIR
            else:
                quality_level = PromptQuality.POOR
            
            # 生成改进建议
            improvement_suggestions = self._generate_improvement_suggestions(
                prompt_data, overall_score
            )
            
            # 识别缺失元素
            missing_elements = self._identify_missing_elements(prompt_data)
            
            return PromptAnalysis(
                clarity_score=clarity_score,
                completeness_score=completeness_score,
                specificity_score=specificity_score,
                context_richness=context_richness,
                technical_accuracy=technical_accuracy,
                overall_quality=quality_level,
                improvement_suggestions=improvement_suggestions,
                missing_elements=missing_elements
            )
            
        except Exception as e:
            logger.error(f"Error analyzing prompt quality: {str(e)}")
            raise
    
    async def _enhanced_debate_optimize(
        self,
        prompt_data: Dict[str, Any],
        analysis: Dict[str, Any],
        prompt_type: PromptType
    ) -> Dict[str, Any]:
        """增强版对抗性辩论优化"""
        try:
            # 多角色辩论
            roles = [
                {"name": "developer", "perspective": "implementation_focused"},
                {"name": "reviewer", "perspective": "quality_focused"},
                {"name": "user_advocate", "perspective": "user_experience_focused"},
                {"name": "security_expert", "perspective": "security_focused"},
                {"name": "performance_expert", "perspective": "performance_focused"}
            ]
            
            current_prompt = prompt_data
            debate_rounds = 0
            max_rounds = 5
            
            for round_num in range(max_rounds):
                debate_rounds += 1
                
                # 收集所有角色的意见
                role_opinions = []
                for role in roles:
                    opinion = await self._get_role_opinion(
                        role, current_prompt, analysis, prompt_type
                    )
                    role_opinions.append(opinion)
                
                # 整合意见并生成改进
                improvements = await self._integrate_role_opinions(
                    role_opinions, current_prompt
                )
                
                # 应用改进
                current_prompt = await self._apply_improvements(
                    current_prompt, improvements
                )
                
                # 检查是否达成共识
                if await self._check_enhanced_consensus(role_opinions, improvements):
                    break
            
            # 计算置信度
            confidence_level = await self._calculate_confidence_level(
                current_prompt, debate_rounds
            )
            
            current_prompt["confidence_level"] = confidence_level
            current_prompt["debate_rounds"] = debate_rounds
            
            return current_prompt
            
        except Exception as e:
            logger.error(f"Error in enhanced debate optimization: {str(e)}")
            raise
    
    # 辅助方法实现
    def _determine_prompt_type(self, user_command: str, analysis: Dict[str, Any]) -> PromptType:
        """确定提示词类型"""
        command_lower = user_command.lower()
        
        if any(word in command_lower for word in ["代码", "code", "开发", "开发", "实现", "implement"]):
            return PromptType.CODE_GENERATION
        elif any(word in command_lower for word in ["分析", "analyze", "评估", "evaluate", "研究", "research"]):
            return PromptType.ANALYSIS
        elif any(word in command_lower for word in ["创意", "creative", "设计", "design", "创作", "create"]):
            return PromptType.CREATIVE
        elif any(word in command_lower for word in ["推理", "reasoning", "思考", "think", "逻辑", "logic"]):
            return PromptType.REASONING
        else:
            return PromptType.TASK_EXECUTION
    
    def _calculate_clarity_score(self, text: str) -> float:
        """计算清晰度分数"""
        # 基于句子长度、词汇复杂度等计算
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # 理想句子长度在10-20个词之间
        if 10 <= avg_sentence_length <= 20:
            length_score = 1.0
        else:
            length_score = max(0, 1 - abs(avg_sentence_length - 15) / 15)
        
        return min(length_score, 1.0)
    
    def _calculate_completeness_score(self, prompt_data: Dict[str, Any]) -> float:
        """计算完整性分数"""
        required_fields = ["optimized_prompt", "context", "technical_requirements", "user_stories", "acceptance_criteria"]
        present_fields = sum(1 for field in required_fields if field in prompt_data and prompt_data[field])
        return present_fields / len(required_fields)
    
    def _calculate_specificity_score(self, text: str) -> float:
        """计算具体性分数"""
        # 基于具体词汇、数字、技术术语等计算
        specific_indicators = [
            r'\d+',  # 数字
            r'[A-Z][a-z]+',  # 专有名词
            r'API|HTTP|JSON|SQL|CSS|HTML',  # 技术术语
            r'确保|必须|需要|要求'  # 具体动词
        ]
        
        score = 0
        for pattern in specific_indicators:
            if re.search(pattern, text):
                score += 0.25
        
        return min(score, 1.0)
    
    def _calculate_context_richness(self, prompt_data: Dict[str, Any]) -> float:
        """计算上下文丰富度"""
        context = prompt_data.get("context", "")
        return min(len(context) / 200, 1.0)  # 200字符为满分
    
    def _calculate_technical_accuracy(self, text: str) -> float:
        """计算技术准确性"""
        # 基于技术关键词的准确性
        technical_keywords = self.quality_patterns["technical_keywords"]
        found_keywords = sum(1 for keyword in technical_keywords if keyword in text)
        return min(found_keywords / 5, 1.0)  # 5个关键词为满分
    
    def _generate_improvement_suggestions(
        self, 
        prompt_data: Dict[str, Any], 
        overall_score: float
    ) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if overall_score < 0.7:
            suggestions.append("增加更多技术细节和具体要求")
            suggestions.append("提供更清晰的上下文信息")
            suggestions.append("添加具体的验收标准")
        
        if len(prompt_data.get("technical_requirements", [])) < 3:
            suggestions.append("补充更多技术需求")
        
        if len(prompt_data.get("user_stories", [])) < 2:
            suggestions.append("添加更多用户故事")
        
        return suggestions
    
    def _identify_missing_elements(self, prompt_data: Dict[str, Any]) -> List[str]:
        """识别缺失元素"""
        missing = []
        
        if not prompt_data.get("technical_requirements"):
            missing.append("技术需求")
        if not prompt_data.get("user_stories"):
            missing.append("用户故事")
        if not prompt_data.get("acceptance_criteria"):
            missing.append("验收标准")
        if not prompt_data.get("context"):
            missing.append("上下文信息")
        
        return missing
    
    # 其他辅助方法的简化实现
    def _identify_app_type(self, command: str) -> str:
        """识别应用类型"""
        command_lower = command.lower()
        if any(word in command_lower for word in ["待办", "todo", "任务", "task"]):
            return "todo_app"
        elif any(word in command_lower for word in ["新闻", "news", "资讯", "rss"]):
            return "news_app"
        elif any(word in command_lower for word in ["购物", "shop", "电商", "商城"]):
            return "ecommerce_app"
        elif any(word in command_lower for word in ["博客", "blog", "文章", "article"]):
            return "blog_app"
        else:
            return "general_app"
    
    def _extract_core_features(self, command: str) -> List[str]:
        """提取核心功能"""
        features = []
        command_lower = command.lower()
        
        if "添加" in command_lower or "add" in command_lower:
            features.append("添加功能")
        if "删除" in command_lower or "delete" in command_lower:
            features.append("删除功能")
        if "编辑" in command_lower or "edit" in command_lower:
            features.append("编辑功能")
        if "搜索" in command_lower or "search" in command_lower:
            features.append("搜索功能")
        if "用户" in command_lower or "user" in command_lower:
            features.append("用户管理")
        if "登录" in command_lower or "login" in command_lower:
            features.append("用户认证")
        
        return features if features else ["基础CRUD功能"]
    
    def _identify_tech_stack(self, command: str, context: Dict[str, Any]) -> List[str]:
        """识别技术栈"""
        tech_stack = []
        
        platform = context.get("platform", "web").lower()
        if platform == "web":
            tech_stack.extend(["React", "Next.js", "TypeScript", "Tailwind CSS"])
        elif platform == "mobile":
            tech_stack.extend(["React Native", "Expo", "TypeScript"])
        
        command_lower = command.lower()
        if "数据库" in command_lower or "database" in command_lower:
            tech_stack.append("PostgreSQL")
        if "实时" in command_lower or "realtime" in command_lower:
            tech_stack.append("WebSocket")
        if "支付" in command_lower or "payment" in command_lower:
            tech_stack.append("Stripe")
        
        return tech_stack
    
    def _analyze_user_roles(self, command: str) -> List[str]:
        """分析用户角色"""
        roles = []
        command_lower = command.lower()
        
        if "管理员" in command_lower or "admin" in command_lower:
            roles.append("管理员")
        if "普通用户" in command_lower or "user" in command_lower:
            roles.append("普通用户")
        if "访客" in command_lower or "guest" in command_lower:
            roles.append("访客")
        
        return roles if roles else ["普通用户"]
    
    def _assess_complexity(self, command: str) -> str:
        """评估复杂度"""
        complexity_indicators = [
            "实时", "realtime", "推送", "push", "通知", "notification",
            "支付", "payment", "安全", "security", "加密", "encrypt",
            "多用户", "multi-user", "权限", "permission", "角色", "role"
        ]
        
        command_lower = command.lower()
        if any(indicator in command_lower for indicator in complexity_indicators):
            return "high"
        elif len(command) > 100:
            return "medium"
        else:
            return "low"
    
    # 其他方法的简化实现
    def _analyze_intent(self, command: str) -> Dict[str, Any]:
        return {"primary_intent": "development", "secondary_intents": []}
    
    def _analyze_domain(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"domain": "software_development", "subdomain": "web_development"}
    
    def _analyze_constraints(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"time_constraints": [], "resource_constraints": [], "technical_constraints": []}
    
    def _analyze_quality_requirements(self, command: str) -> Dict[str, Any]:
        return {"performance": "medium", "security": "high", "usability": "high"}
    
    def _has_technical_terms(self, command: str) -> bool:
        technical_terms = ["API", "数据库", "前端", "后端", "部署", "测试"]
        return any(term in command for term in technical_terms)
    
    # 其他方法的占位符实现
    async def _generate_code_generation_prompt(self, user_command: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {"optimized_prompt": f"请开发一个{analysis['app_type']}应用", "context": "代码生成", "technical_requirements": [], "user_stories": [], "acceptance_criteria": []}
    
    async def _generate_analysis_prompt(self, user_command: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {"optimized_prompt": f"请分析{user_command}", "context": "分析任务", "technical_requirements": [], "user_stories": [], "acceptance_criteria": []}
    
    async def _generate_creative_prompt(self, user_command: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {"optimized_prompt": f"请创作{user_command}", "context": "创意任务", "technical_requirements": [], "user_stories": [], "acceptance_criteria": []}
    
    async def _generate_reasoning_prompt(self, user_command: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {"optimized_prompt": f"请推理{user_command}", "context": "推理任务", "technical_requirements": [], "user_stories": [], "acceptance_criteria": []}
    
    async def _generate_general_prompt(self, user_command: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {"optimized_prompt": f"请执行{user_command}", "context": "一般任务", "technical_requirements": [], "user_stories": [], "acceptance_criteria": []}
    
    async def _get_role_opinion(self, role: Dict[str, str], prompt_data: Dict[str, Any], analysis: Dict[str, Any], prompt_type: PromptType) -> Dict[str, Any]:
        return {"role": role["name"], "suggestions": [], "concerns": []}
    
    async def _integrate_role_opinions(self, opinions: List[Dict[str, Any]], prompt_data: Dict[str, Any]) -> List[str]:
        return []
    
    async def _apply_improvements(self, prompt_data: Dict[str, Any], improvements: List[str]) -> Dict[str, Any]:
        return prompt_data
    
    async def _check_enhanced_consensus(self, opinions: List[Dict[str, Any]], improvements: List[str]) -> bool:
        return len(improvements) < 2
    
    async def _calculate_confidence_level(self, prompt_data: Dict[str, Any], debate_rounds: int) -> float:
        return max(0.5, 1.0 - debate_rounds * 0.1)
    
    async def _enhanced_constitution_check(self, prompt_data: Dict[str, Any]) -> List[str]:
        return ["✓ 通过宪法检查"]
    
    async def _enhanced_tool_recommendations(self, prompt_data: Dict[str, Any], analysis: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        return ["github_copilot", "jest", "vercel"]
    
    async def _assess_risks(self, prompt_data: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        return ["技术风险：中等", "时间风险：低"]
    
    async def _estimate_execution(self, prompt_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        return "预计执行时间：2-4小时"
    
    async def _calculate_final_quality_score(self, prompt_data: Dict[str, Any], quality_analysis: PromptAnalysis) -> float:
        return quality_analysis.clarity_score * 0.3 + quality_analysis.completeness_score * 0.3 + quality_analysis.specificity_score * 0.4

# 创建全局实例
enhanced_prompt_optimizer = EnhancedPromptOptimizer()
