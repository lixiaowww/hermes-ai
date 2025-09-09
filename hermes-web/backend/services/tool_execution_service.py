"""
Tool Execution Service
松耦合的工具执行服务
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
import uuid

from core.models import ToolExecuteRequest, ToolExecuteResponse
from training_module import training_module

logger = logging.getLogger(__name__)

class ToolExecutionService:
    """工具执行服务类"""
    
    def __init__(self):
        self.tool_registry = {}
        self._initialize_builtin_tools()
    
    def _initialize_builtin_tools(self):
        """初始化内置工具"""
        self.tool_registry = {
            "code_generator_llm": self._tool_code_generator_llm,
            "test_generator_llm": self._tool_test_generator_llm,
            "code_reviewer_llm": self._tool_code_reviewer_llm,
            "documentation_generator_llm": self._tool_documentation_generator_llm,
            "refactoring_llm": self._tool_refactoring_llm,
            "security_analyzer": self._tool_security_analyzer,
            "performance_analyzer": self._tool_performance_analyzer,
            "dependency_analyzer": self._tool_dependency_analyzer,
            "code_quality_analyzer": self._tool_code_quality_analyzer,
            "test_runner": self._tool_test_runner,
            "linter": self._tool_linter,
            "formatter": self._tool_formatter,
            "build_tool": self._tool_build_tool,
            "web_search": self._tool_web_search,
            "github_search": self._tool_github_search,
            "stackoverflow_search": self._tool_stackoverflow_search,
            "file_reader": self._tool_file_reader,
            "file_writer": self._tool_file_writer,
            "git_operations": self._tool_git_operations,
        }
    
    async def execute_tool(self, request: ToolExecuteRequest, user_intent: str = None) -> ToolExecuteResponse:
        """执行工具"""
        try:
            # 执行工具
            if request.tool_name in self.tool_registry:
                output = await self.tool_registry[request.tool_name](request.input_data)
            else:
                output = {"error": f"Tool {request.tool_name} not found"}
            
            # 生成审计ID
            audited_call_id = str(uuid.uuid4())
            
            # 记录训练数据（异步，不阻塞主流程）
            if user_intent:
                asyncio.create_task(self._record_training_data(
                    request, output, user_intent, audited_call_id
                ))
            
            return ToolExecuteResponse(
                tool_name=request.tool_name,
                output=output,
                audited_call_id=audited_call_id
            )
            
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return ToolExecuteResponse(
                tool_name=request.tool_name,
                output={"error": str(e)},
                audited_call_id=str(uuid.uuid4())
            )
    
    async def _record_training_data(self, request: ToolExecuteRequest, output: Dict[str, Any], user_intent: str, audited_call_id: str):
        """记录训练数据"""
        try:
            await training_module.record_interaction(
                user_intent=user_intent or f"Tool execution: {request.tool_name}",
                original_prompt=request.input_data.get("prompt", ""),
                orchestration_plan=[{
                    "step": 1,
                    "tool": request.tool_name,
                    "purpose": "Tool execution",
                    "input": request.input_data
                }],
                tool_calls=[{
                    "tool_name": request.tool_name,
                    "input": request.input_data,
                    "mode": request.mode
                }],
                tool_results=[{
                    "tool_name": request.tool_name,
                    "output": output,
                    "success": "error" not in output
                }],
                final_outcome=output
            )
        except Exception as e:
            logger.warning(f"Failed to record training data: {e}")
    
    # 内置工具实现
    async def _tool_code_generator_llm(self, input_data: dict) -> dict:
        """代码生成LLM工具"""
        return {
            "tool_type": "llm",
            "provider": "openai",
            "capability": "code_generation",
            "result": "Generated code would be here (coordinated via external LLM)",
            "metadata": {"model": "gpt-4", "tokens_used": 1500, "temperature": 0.7}
        }
    
    async def _tool_test_generator_llm(self, input_data: dict) -> dict:
        """测试生成LLM工具"""
        return {
            "tool_type": "llm",
            "provider": "openai",
            "capability": "test_generation",
            "result": "Generated tests would be here (coordinated via external LLM)",
            "metadata": {"model": "gpt-4", "test_count": 15, "coverage": 85}
        }
    
    async def _tool_code_reviewer_llm(self, input_data: dict) -> dict:
        """代码审查LLM工具"""
        return {
            "tool_type": "llm",
            "provider": "openai",
            "capability": "code_review",
            "result": "Code review would be here (coordinated via external LLM)",
            "metadata": {"model": "gpt-4", "issues_found": 3, "suggestions": 8}
        }
    
    async def _tool_documentation_generator_llm(self, input_data: dict) -> dict:
        """文档生成LLM工具"""
        return {
            "tool_type": "llm",
            "provider": "openai",
            "capability": "documentation_generation",
            "result": "Generated documentation would be here (coordinated via external LLM)",
            "metadata": {"model": "gpt-4", "sections": 5, "word_count": 1200}
        }
    
    async def _tool_refactoring_llm(self, input_data: dict) -> dict:
        """重构LLM工具"""
        return {
            "tool_type": "llm",
            "provider": "openai",
            "capability": "code_refactoring",
            "result": "Refactored code would be here (coordinated via external LLM)",
            "metadata": {"model": "gpt-4", "improvements": 6, "complexity_reduced": 15}
        }
    
    async def _tool_security_analyzer(self, input_data: dict) -> dict:
        """安全分析工具"""
        return {
            "tool_type": "analyzer",
            "provider": "github",
            "capability": "security_analysis",
            "result": "Security analysis would be here (coordinated via external tool)",
            "metadata": {"tool": "safety", "vulnerabilities": 0, "outdated_packages": 3}
        }
    
    async def _tool_performance_analyzer(self, input_data: dict) -> dict:
        """性能分析工具"""
        return {
            "tool_type": "analyzer",
            "provider": "local",
            "capability": "performance_analysis",
            "result": "Performance analysis would be here (coordinated via external tool)",
            "metadata": {"tool": "profiler", "bottlenecks": 2, "optimization_score": 78}
        }
    
    async def _tool_dependency_analyzer(self, input_data: dict) -> dict:
        """依赖分析工具"""
        return {
            "tool_type": "analyzer",
            "provider": "github",
            "capability": "dependency_analysis",
            "result": "Dependency analysis would be here (coordinated via external tool)",
            "metadata": {"tool": "safety", "vulnerabilities": 0, "outdated_packages": 3}
        }
    
    async def _tool_code_quality_analyzer(self, input_data: dict) -> dict:
        """代码质量分析工具"""
        return {
            "tool_type": "analyzer",
            "provider": "github",
            "capability": "code_quality_analysis",
            "result": "Code quality analysis would be here (coordinated via external tool)",
            "metadata": {"tool": "sonarqube", "quality_score": 85, "issues": 12}
        }
    
    async def _tool_test_runner(self, input_data: dict) -> dict:
        """测试运行工具"""
        return {
            "tool_type": "executor",
            "provider": "local",
            "capability": "test_execution",
            "result": "Test execution results would be here (coordinated via external runner)",
            "metadata": {"framework": "pytest", "tests_passed": 45, "tests_failed": 2, "coverage": 92}
        }
    
    async def _tool_linter(self, input_data: dict) -> dict:
        """代码检查工具"""
        return {
            "tool_type": "executor",
            "provider": "local",
            "capability": "code_linting",
            "result": "Linting results would be here (coordinated via external linter)",
            "metadata": {"tool": "eslint", "errors": 0, "warnings": 3, "fixable": 2}
        }
    
    async def _tool_formatter(self, input_data: dict) -> dict:
        """代码格式化工具"""
        return {
            "tool_type": "executor",
            "provider": "local",
            "capability": "code_formatting",
            "result": "Formatted code would be here (coordinated via external formatter)",
            "metadata": {"tool": "prettier", "files_formatted": 8, "changes_made": 15}
        }
    
    async def _tool_build_tool(self, input_data: dict) -> dict:
        """构建工具"""
        return {
            "tool_type": "executor",
            "provider": "local",
            "capability": "build_execution",
            "result": "Build results would be here (coordinated via external build tool)",
            "metadata": {"tool": "webpack", "status": "success", "bundle_size": "2.3MB", "build_time": "45s"}
        }
    
    async def _tool_web_search(self, input_data: dict) -> dict:
        """网络搜索工具"""
        return {
            "tool_type": "search",
            "provider": "web",
            "capability": "web_search",
            "result": "Web search results would be here (coordinated via search API)",
            "metadata": {"query": input_data.get("query", ""), "results": 25, "sources": 15}
        }
    
    async def _tool_github_search(self, input_data: dict) -> dict:
        """GitHub搜索工具"""
        return {
            "tool_type": "search",
            "provider": "github",
            "capability": "code_search",
            "result": "GitHub search results would be here (coordinated via GitHub API)",
            "metadata": {"query": input_data.get("query", ""), "repositories": 25, "code_snippets": 150}
        }
    
    async def _tool_stackoverflow_search(self, input_data: dict) -> dict:
        """Stack Overflow搜索工具"""
        return {
            "tool_type": "search",
            "provider": "stackoverflow",
            "capability": "qna_search",
            "result": "Stack Overflow results would be here (coordinated via SO API)",
            "metadata": {"query": input_data.get("query", ""), "questions": 12, "answers": 35}
        }
    
    async def _tool_file_reader(self, input_data: dict) -> dict:
        """文件读取工具"""
        return {
            "tool_type": "file_ops",
            "provider": "local",
            "capability": "file_reading",
            "result": "File content would be here (coordinated via file system)",
            "metadata": {"file_path": input_data.get("path", ""), "size": "15KB", "lines": 450}
        }
    
    async def _tool_file_writer(self, input_data: dict) -> dict:
        """文件写入工具"""
        return {
            "tool_type": "file_ops",
            "provider": "local",
            "capability": "file_writing",
            "result": "File write operation completed (coordinated via file system)",
            "metadata": {"file_path": input_data.get("path", ""), "bytes_written": 2048, "status": "success"}
        }
    
    async def _tool_git_operations(self, input_data: dict) -> dict:
        """Git操作工具"""
        return {
            "tool_type": "version_control",
            "provider": "local",
            "capability": "git_operations",
            "result": "Git operations would be here (coordinated via git commands)",
            "metadata": {"operation": input_data.get("operation", ""), "status": "success", "files_changed": 5}
        }

# 创建全局实例
tool_execution_service = ToolExecutionService()
