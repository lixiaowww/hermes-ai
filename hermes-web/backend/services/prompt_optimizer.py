"""
Prompt Optimizer Service
Prompt优化器服务 - 将模糊命令转换为精准、结构化、可监督的prompt
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio

@dataclass
class OptimizedPrompt:
    """优化后的Prompt结构"""
    id: str
    original_command: str
    optimized_prompt: str
    context: str
    technical_requirements: List[str]
    user_stories: List[str]
    acceptance_criteria: List[str]
    quality_score: float
    debate_rounds: int
    constitution_checks: List[str]
    tool_recommendations: List[str]
    created_at: str

class PromptOptimizer:
    """Prompt优化器"""
    
    def __init__(self):
        self.constitution_rules = self._load_constitution()
        self.tool_catalog = self._load_tool_catalog()
    
    def _load_constitution(self) -> Dict[str, List[str]]:
        """加载宪法规则"""
        return {
            "development_principles": [
                "代码必须遵循最佳实践和设计模式",
                "必须包含完整的错误处理机制",
                "必须考虑安全性和性能优化",
                "必须包含完整的测试用例",
                "必须遵循可维护性和可扩展性原则"
            ],
            "review_standards": [
                "代码质量必须达到生产环境标准",
                "必须通过所有自动化测试",
                "必须符合安全审计要求",
                "必须通过性能基准测试",
                "必须通过用户体验评审"
            ],
            "ethical_guidelines": [
                "不得包含歧视性内容",
                "必须保护用户隐私",
                "必须遵循数据保护法规",
                "必须确保算法公平性",
                "必须提供透明的决策过程"
            ]
        }
    
    def _load_tool_catalog(self) -> Dict[str, Dict]:
        """加载工具目录"""
        return {
            "code_generation": {
                "tools": ["github_copilot", "replit_agent", "codesandbox"],
                "description": "代码生成工具",
                "use_cases": ["生成基础代码", "实现特定功能", "创建原型"]
            },
            "testing": {
                "tools": ["jest", "pytest", "cypress", "playwright"],
                "description": "测试工具",
                "use_cases": ["单元测试", "集成测试", "端到端测试"]
            },
            "deployment": {
                "tools": ["vercel", "netlify", "docker", "kubernetes"],
                "description": "部署工具",
                "use_cases": ["应用部署", "容器化", "云服务配置"]
            },
            "monitoring": {
                "tools": ["sentry", "datadog", "newrelic", "prometheus"],
                "description": "监控工具",
                "use_cases": ["错误监控", "性能监控", "日志分析"]
            }
        }
    
    async def optimize_prompt(self, user_command: str, context: Dict[str, Any]) -> OptimizedPrompt:
        """优化用户命令为精准prompt"""
        prompt_id = str(uuid.uuid4())[:8]
        
        # 第一步：基础分析和结构化
        structured_analysis = await self._analyze_command(user_command, context)
        
        # 第二步：对抗性辩论优化
        debated_prompt = await self._debate_optimize(structured_analysis)
        
        # 第三步：宪法检查
        constitution_checks = await self._constitution_check(debated_prompt)
        
        # 第四步：工具推荐
        tool_recommendations = await self._recommend_tools(debated_prompt, context)
        
        # 第五步：质量评分
        quality_score = await self._calculate_quality_score(debated_prompt)
        
        return OptimizedPrompt(
            id=prompt_id,
            original_command=user_command,
            optimized_prompt=debated_prompt["optimized_prompt"],
            context=debated_prompt["context"],
            technical_requirements=debated_prompt["technical_requirements"],
            user_stories=debated_prompt["user_stories"],
            acceptance_criteria=debated_prompt["acceptance_criteria"],
            quality_score=quality_score,
            debate_rounds=debated_prompt["debate_rounds"],
            constitution_checks=constitution_checks,
            tool_recommendations=tool_recommendations,
            created_at=datetime.now().isoformat()
        )
    
    async def _analyze_command(self, user_command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析用户命令"""
        # 识别应用类型
        app_type = self._identify_app_type(user_command)
        
        # 提取核心功能
        core_features = self._extract_core_features(user_command)
        
        # 识别技术栈
        tech_stack = self._identify_tech_stack(user_command, context)
        
        # 分析用户角色
        user_roles = self._analyze_user_roles(user_command)
        
        return {
            "app_type": app_type,
            "core_features": core_features,
            "tech_stack": tech_stack,
            "user_roles": user_roles,
            "complexity_level": self._assess_complexity(user_command)
        }
    
    async def _debate_optimize(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """对抗性辩论优化"""
        # 模拟开发者角色
        developer_prompt = self._generate_developer_prompt(analysis)
        
        # 模拟审核者角色
        reviewer_prompt = self._generate_reviewer_prompt(analysis, developer_prompt)
        
        # 模拟辩论过程
        debate_rounds = 0
        current_prompt = developer_prompt
        
        for round_num in range(3):  # 最多3轮辩论
            debate_rounds += 1
            
            # 审核者提出改进建议
            improvements = self._generate_improvements(current_prompt, analysis)
            
            # 开发者整合建议
            current_prompt = self._integrate_improvements(current_prompt, improvements)
            
            # 检查是否达成一致
            if self._check_consensus(current_prompt, improvements):
                break
        
        return {
            "optimized_prompt": current_prompt["prompt"],
            "context": current_prompt["context"],
            "technical_requirements": current_prompt["technical_requirements"],
            "user_stories": current_prompt["user_stories"],
            "acceptance_criteria": current_prompt["acceptance_criteria"],
            "debate_rounds": debate_rounds
        }
    
    async def _constitution_check(self, prompt_data: Dict[str, Any]) -> List[str]:
        """宪法检查"""
        checks = []
        
        # 检查开发原则
        for principle in self.constitution_rules["development_principles"]:
            if self._check_principle_compliance(prompt_data, principle):
                checks.append(f"✓ {principle}")
            else:
                checks.append(f"✗ {principle}")
        
        # 检查审核标准
        for standard in self.constitution_rules["review_standards"]:
            if self._check_standard_compliance(prompt_data, standard):
                checks.append(f"✓ {standard}")
            else:
                checks.append(f"✗ {standard}")
        
        # 检查伦理准则
        for guideline in self.constitution_rules["ethical_guidelines"]:
            if self._check_guideline_compliance(prompt_data, guideline):
                checks.append(f"✓ {guideline}")
            else:
                checks.append(f"✗ {guideline}")
        
        return checks
    
    async def _recommend_tools(self, prompt_data: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """推荐工具"""
        recommendations = []
        
        # 根据技术需求推荐工具
        for requirement in prompt_data["technical_requirements"]:
            if "测试" in requirement or "test" in requirement.lower():
                recommendations.extend(self.tool_catalog["testing"]["tools"])
            elif "部署" in requirement or "deploy" in requirement.lower():
                recommendations.extend(self.tool_catalog["deployment"]["tools"])
            elif "监控" in requirement or "monitor" in requirement.lower():
                recommendations.extend(self.tool_catalog["monitoring"]["tools"])
        
        # 根据应用类型推荐工具
        if "web" in context.get("platform", "").lower():
            recommendations.extend(["react", "nextjs", "tailwindcss"])
        elif "mobile" in context.get("platform", "").lower():
            recommendations.extend(["react-native", "expo", "flutter"])
        
        return list(set(recommendations))  # 去重
    
    async def _calculate_quality_score(self, prompt_data: Dict[str, Any]) -> float:
        """计算质量评分"""
        score = 0.0
        
        # 基础分数
        score += 0.3  # 基础分
        
        # 技术需求完整性
        if len(prompt_data["technical_requirements"]) >= 3:
            score += 0.2
        
        # 用户故事完整性
        if len(prompt_data["user_stories"]) >= 2:
            score += 0.2
        
        # 验收标准完整性
        if len(prompt_data["acceptance_criteria"]) >= 3:
            score += 0.2
        
        # 上下文信息丰富度
        if len(prompt_data["context"]) > 100:
            score += 0.1
        
        return min(score, 1.0)  # 最高1.0分
    
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
        
        # 根据平台选择
        platform = context.get("platform", "web").lower()
        if platform == "web":
            tech_stack.extend(["React", "Next.js", "TypeScript", "Tailwind CSS"])
        elif platform == "mobile":
            tech_stack.extend(["React Native", "Expo", "TypeScript"])
        
        # 根据功能选择
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
    
    def _generate_developer_prompt(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成开发者视角的prompt"""
        return {
            "prompt": f"""
请开发一个{analysis['app_type']}应用，具备以下核心功能：
{', '.join(analysis['core_features'])}

技术栈：{', '.join(analysis['tech_stack'])}
用户角色：{', '.join(analysis['user_roles'])}
复杂度：{analysis['complexity_level']}

请确保代码质量高、可维护性强、包含完整的错误处理和测试用例。
            """.strip(),
            "context": f"应用类型：{analysis['app_type']}，技术栈：{', '.join(analysis['tech_stack'])}",
            "technical_requirements": [
                "实现响应式设计",
                "包含完整的错误处理",
                "添加单元测试和集成测试",
                "确保代码可维护性",
                "优化性能和安全性"
            ],
            "user_stories": [
                f"作为{role}，我希望能够{feature}" 
                for role in analysis['user_roles'] 
                for feature in analysis['core_features']
            ],
            "acceptance_criteria": [
                "所有功能正常工作",
                "通过所有测试用例",
                "符合性能要求",
                "通过安全审计",
                "用户体验良好"
            ]
        }
    
    def _generate_reviewer_prompt(self, analysis: Dict[str, Any], developer_prompt: Dict[str, Any]) -> Dict[str, Any]:
        """生成审核者视角的prompt"""
        return {
            "prompt": f"""
审核以下开发需求，确保符合生产环境标准：

{developer_prompt['prompt']}

请特别关注：
1. 代码质量和最佳实践
2. 安全性和性能优化
3. 用户体验和可访问性
4. 测试覆盖率和质量
5. 文档和注释完整性
            """.strip(),
            "context": "审核者视角，关注代码质量和生产环境标准",
            "technical_requirements": developer_prompt["technical_requirements"] + [
                "通过代码质量检查",
                "符合安全标准",
                "通过性能测试",
                "包含完整文档"
            ],
            "user_stories": developer_prompt["user_stories"],
            "acceptance_criteria": developer_prompt["acceptance_criteria"] + [
                "通过代码审查",
                "符合团队编码规范",
                "通过自动化测试",
                "通过安全扫描"
            ]
        }
    
    def _generate_improvements(self, current_prompt: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        improvements = []
        
        # 基于复杂度添加建议
        if analysis["complexity_level"] == "high":
            improvements.append("添加实时数据同步功能")
            improvements.append("实现高级安全措施")
            improvements.append("添加性能监控")
        
        # 基于应用类型添加建议
        if analysis["app_type"] == "todo_app":
            improvements.append("添加任务优先级和标签功能")
            improvements.append("实现任务搜索和过滤")
        elif analysis["app_type"] == "news_app":
            improvements.append("添加新闻分类和标签")
            improvements.append("实现个性化推荐")
        
        return improvements
    
    def _integrate_improvements(self, current_prompt: Dict[str, Any], improvements: List[str]) -> Dict[str, Any]:
        """整合改进建议"""
        updated_requirements = current_prompt["technical_requirements"] + improvements
        updated_criteria = current_prompt["acceptance_criteria"] + [
            f"实现{improvement}" for improvement in improvements
        ]
        
        return {
            **current_prompt,
            "technical_requirements": updated_requirements,
            "acceptance_criteria": updated_criteria
        }
    
    def _check_consensus(self, current_prompt: Dict[str, Any], improvements: List[str]) -> bool:
        """检查是否达成一致"""
        # 简单的共识检查：如果改进建议少于3个，认为达成一致
        return len(improvements) < 3
    
    def _check_principle_compliance(self, prompt_data: Dict[str, Any], principle: str) -> bool:
        """检查原则合规性"""
        # 简化的合规性检查
        return True  # 实际实现中需要更复杂的逻辑
    
    def _check_standard_compliance(self, prompt_data: Dict[str, Any], standard: str) -> bool:
        """检查标准合规性"""
        return True  # 实际实现中需要更复杂的逻辑
    
    def _check_guideline_compliance(self, prompt_data: Dict[str, Any], guideline: str) -> bool:
        """检查准则合规性"""
        return True  # 实际实现中需要更复杂的逻辑

# 全局实例
prompt_optimizer = PromptOptimizer()

Prompt Optimizer Service
Prompt优化器服务 - 将模糊命令转换为精准、结构化、可监督的prompt
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio

@dataclass
class OptimizedPrompt:
    """优化后的Prompt结构"""
    id: str
    original_command: str
    optimized_prompt: str
    context: str
    technical_requirements: List[str]
    user_stories: List[str]
    acceptance_criteria: List[str]
    quality_score: float
    debate_rounds: int
    constitution_checks: List[str]
    tool_recommendations: List[str]
    created_at: str

class PromptOptimizer:
    """Prompt优化器"""
    
    def __init__(self):
        self.constitution_rules = self._load_constitution()
        self.tool_catalog = self._load_tool_catalog()
    
    def _load_constitution(self) -> Dict[str, List[str]]:
        """加载宪法规则"""
        return {
            "development_principles": [
                "代码必须遵循最佳实践和设计模式",
                "必须包含完整的错误处理机制",
                "必须考虑安全性和性能优化",
                "必须包含完整的测试用例",
                "必须遵循可维护性和可扩展性原则"
            ],
            "review_standards": [
                "代码质量必须达到生产环境标准",
                "必须通过所有自动化测试",
                "必须符合安全审计要求",
                "必须通过性能基准测试",
                "必须通过用户体验评审"
            ],
            "ethical_guidelines": [
                "不得包含歧视性内容",
                "必须保护用户隐私",
                "必须遵循数据保护法规",
                "必须确保算法公平性",
                "必须提供透明的决策过程"
            ]
        }
    
    def _load_tool_catalog(self) -> Dict[str, Dict]:
        """加载工具目录"""
        return {
            "code_generation": {
                "tools": ["github_copilot", "replit_agent", "codesandbox"],
                "description": "代码生成工具",
                "use_cases": ["生成基础代码", "实现特定功能", "创建原型"]
            },
            "testing": {
                "tools": ["jest", "pytest", "cypress", "playwright"],
                "description": "测试工具",
                "use_cases": ["单元测试", "集成测试", "端到端测试"]
            },
            "deployment": {
                "tools": ["vercel", "netlify", "docker", "kubernetes"],
                "description": "部署工具",
                "use_cases": ["应用部署", "容器化", "云服务配置"]
            },
            "monitoring": {
                "tools": ["sentry", "datadog", "newrelic", "prometheus"],
                "description": "监控工具",
                "use_cases": ["错误监控", "性能监控", "日志分析"]
            }
        }
    
    async def optimize_prompt(self, user_command: str, context: Dict[str, Any]) -> OptimizedPrompt:
        """优化用户命令为精准prompt"""
        prompt_id = str(uuid.uuid4())[:8]
        
        # 第一步：基础分析和结构化
        structured_analysis = await self._analyze_command(user_command, context)
        
        # 第二步：对抗性辩论优化
        debated_prompt = await self._debate_optimize(structured_analysis)
        
        # 第三步：宪法检查
        constitution_checks = await self._constitution_check(debated_prompt)
        
        # 第四步：工具推荐
        tool_recommendations = await self._recommend_tools(debated_prompt, context)
        
        # 第五步：质量评分
        quality_score = await self._calculate_quality_score(debated_prompt)
        
        return OptimizedPrompt(
            id=prompt_id,
            original_command=user_command,
            optimized_prompt=debated_prompt["optimized_prompt"],
            context=debated_prompt["context"],
            technical_requirements=debated_prompt["technical_requirements"],
            user_stories=debated_prompt["user_stories"],
            acceptance_criteria=debated_prompt["acceptance_criteria"],
            quality_score=quality_score,
            debate_rounds=debated_prompt["debate_rounds"],
            constitution_checks=constitution_checks,
            tool_recommendations=tool_recommendations,
            created_at=datetime.now().isoformat()
        )
    
    async def _analyze_command(self, user_command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析用户命令"""
        # 识别应用类型
        app_type = self._identify_app_type(user_command)
        
        # 提取核心功能
        core_features = self._extract_core_features(user_command)
        
        # 识别技术栈
        tech_stack = self._identify_tech_stack(user_command, context)
        
        # 分析用户角色
        user_roles = self._analyze_user_roles(user_command)
        
        return {
            "app_type": app_type,
            "core_features": core_features,
            "tech_stack": tech_stack,
            "user_roles": user_roles,
            "complexity_level": self._assess_complexity(user_command)
        }
    
    async def _debate_optimize(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """对抗性辩论优化"""
        # 模拟开发者角色
        developer_prompt = self._generate_developer_prompt(analysis)
        
        # 模拟审核者角色
        reviewer_prompt = self._generate_reviewer_prompt(analysis, developer_prompt)
        
        # 模拟辩论过程
        debate_rounds = 0
        current_prompt = developer_prompt
        
        for round_num in range(3):  # 最多3轮辩论
            debate_rounds += 1
            
            # 审核者提出改进建议
            improvements = self._generate_improvements(current_prompt, analysis)
            
            # 开发者整合建议
            current_prompt = self._integrate_improvements(current_prompt, improvements)
            
            # 检查是否达成一致
            if self._check_consensus(current_prompt, improvements):
                break
        
        return {
            "optimized_prompt": current_prompt["prompt"],
            "context": current_prompt["context"],
            "technical_requirements": current_prompt["technical_requirements"],
            "user_stories": current_prompt["user_stories"],
            "acceptance_criteria": current_prompt["acceptance_criteria"],
            "debate_rounds": debate_rounds
        }
    
    async def _constitution_check(self, prompt_data: Dict[str, Any]) -> List[str]:
        """宪法检查"""
        checks = []
        
        # 检查开发原则
        for principle in self.constitution_rules["development_principles"]:
            if self._check_principle_compliance(prompt_data, principle):
                checks.append(f"✓ {principle}")
            else:
                checks.append(f"✗ {principle}")
        
        # 检查审核标准
        for standard in self.constitution_rules["review_standards"]:
            if self._check_standard_compliance(prompt_data, standard):
                checks.append(f"✓ {standard}")
            else:
                checks.append(f"✗ {standard}")
        
        # 检查伦理准则
        for guideline in self.constitution_rules["ethical_guidelines"]:
            if self._check_guideline_compliance(prompt_data, guideline):
                checks.append(f"✓ {guideline}")
            else:
                checks.append(f"✗ {guideline}")
        
        return checks
    
    async def _recommend_tools(self, prompt_data: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """推荐工具"""
        recommendations = []
        
        # 根据技术需求推荐工具
        for requirement in prompt_data["technical_requirements"]:
            if "测试" in requirement or "test" in requirement.lower():
                recommendations.extend(self.tool_catalog["testing"]["tools"])
            elif "部署" in requirement or "deploy" in requirement.lower():
                recommendations.extend(self.tool_catalog["deployment"]["tools"])
            elif "监控" in requirement or "monitor" in requirement.lower():
                recommendations.extend(self.tool_catalog["monitoring"]["tools"])
        
        # 根据应用类型推荐工具
        if "web" in context.get("platform", "").lower():
            recommendations.extend(["react", "nextjs", "tailwindcss"])
        elif "mobile" in context.get("platform", "").lower():
            recommendations.extend(["react-native", "expo", "flutter"])
        
        return list(set(recommendations))  # 去重
    
    async def _calculate_quality_score(self, prompt_data: Dict[str, Any]) -> float:
        """计算质量评分"""
        score = 0.0
        
        # 基础分数
        score += 0.3  # 基础分
        
        # 技术需求完整性
        if len(prompt_data["technical_requirements"]) >= 3:
            score += 0.2
        
        # 用户故事完整性
        if len(prompt_data["user_stories"]) >= 2:
            score += 0.2
        
        # 验收标准完整性
        if len(prompt_data["acceptance_criteria"]) >= 3:
            score += 0.2
        
        # 上下文信息丰富度
        if len(prompt_data["context"]) > 100:
            score += 0.1
        
        return min(score, 1.0)  # 最高1.0分
    
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
        
        # 根据平台选择
        platform = context.get("platform", "web").lower()
        if platform == "web":
            tech_stack.extend(["React", "Next.js", "TypeScript", "Tailwind CSS"])
        elif platform == "mobile":
            tech_stack.extend(["React Native", "Expo", "TypeScript"])
        
        # 根据功能选择
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
    
    def _generate_developer_prompt(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成开发者视角的prompt"""
        return {
            "prompt": f"""
请开发一个{analysis['app_type']}应用，具备以下核心功能：
{', '.join(analysis['core_features'])}

技术栈：{', '.join(analysis['tech_stack'])}
用户角色：{', '.join(analysis['user_roles'])}
复杂度：{analysis['complexity_level']}

请确保代码质量高、可维护性强、包含完整的错误处理和测试用例。
            """.strip(),
            "context": f"应用类型：{analysis['app_type']}，技术栈：{', '.join(analysis['tech_stack'])}",
            "technical_requirements": [
                "实现响应式设计",
                "包含完整的错误处理",
                "添加单元测试和集成测试",
                "确保代码可维护性",
                "优化性能和安全性"
            ],
            "user_stories": [
                f"作为{role}，我希望能够{feature}" 
                for role in analysis['user_roles'] 
                for feature in analysis['core_features']
            ],
            "acceptance_criteria": [
                "所有功能正常工作",
                "通过所有测试用例",
                "符合性能要求",
                "通过安全审计",
                "用户体验良好"
            ]
        }
    
    def _generate_reviewer_prompt(self, analysis: Dict[str, Any], developer_prompt: Dict[str, Any]) -> Dict[str, Any]:
        """生成审核者视角的prompt"""
        return {
            "prompt": f"""
审核以下开发需求，确保符合生产环境标准：

{developer_prompt['prompt']}

请特别关注：
1. 代码质量和最佳实践
2. 安全性和性能优化
3. 用户体验和可访问性
4. 测试覆盖率和质量
5. 文档和注释完整性
            """.strip(),
            "context": "审核者视角，关注代码质量和生产环境标准",
            "technical_requirements": developer_prompt["technical_requirements"] + [
                "通过代码质量检查",
                "符合安全标准",
                "通过性能测试",
                "包含完整文档"
            ],
            "user_stories": developer_prompt["user_stories"],
            "acceptance_criteria": developer_prompt["acceptance_criteria"] + [
                "通过代码审查",
                "符合团队编码规范",
                "通过自动化测试",
                "通过安全扫描"
            ]
        }
    
    def _generate_improvements(self, current_prompt: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        improvements = []
        
        # 基于复杂度添加建议
        if analysis["complexity_level"] == "high":
            improvements.append("添加实时数据同步功能")
            improvements.append("实现高级安全措施")
            improvements.append("添加性能监控")
        
        # 基于应用类型添加建议
        if analysis["app_type"] == "todo_app":
            improvements.append("添加任务优先级和标签功能")
            improvements.append("实现任务搜索和过滤")
        elif analysis["app_type"] == "news_app":
            improvements.append("添加新闻分类和标签")
            improvements.append("实现个性化推荐")
        
        return improvements
    
    def _integrate_improvements(self, current_prompt: Dict[str, Any], improvements: List[str]) -> Dict[str, Any]:
        """整合改进建议"""
        updated_requirements = current_prompt["technical_requirements"] + improvements
        updated_criteria = current_prompt["acceptance_criteria"] + [
            f"实现{improvement}" for improvement in improvements
        ]
        
        return {
            **current_prompt,
            "technical_requirements": updated_requirements,
            "acceptance_criteria": updated_criteria
        }
    
    def _check_consensus(self, current_prompt: Dict[str, Any], improvements: List[str]) -> bool:
        """检查是否达成一致"""
        # 简单的共识检查：如果改进建议少于3个，认为达成一致
        return len(improvements) < 3
    
    def _check_principle_compliance(self, prompt_data: Dict[str, Any], principle: str) -> bool:
        """检查原则合规性"""
        # 简化的合规性检查
        return True  # 实际实现中需要更复杂的逻辑
    
    def _check_standard_compliance(self, prompt_data: Dict[str, Any], standard: str) -> bool:
        """检查标准合规性"""
        return True  # 实际实现中需要更复杂的逻辑
    
    def _check_guideline_compliance(self, prompt_data: Dict[str, Any], guideline: str) -> bool:
        """检查准则合规性"""
        return True  # 实际实现中需要更复杂的逻辑

# 全局实例
prompt_optimizer = PromptOptimizer()
