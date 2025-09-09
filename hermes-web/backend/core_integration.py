"""
ZSCE Agent Core Integration Module

This module integrates the existing ZSCE Agent core system with the web application,
providing API endpoints for the core agent functionality.
"""

import os
import sys
import subprocess
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# Add the core agent path to sys.path
CORE_AGENT_PATH = Path(__file__).parent.parent.parent / "zswe-agent"
sys.path.insert(0, str(CORE_AGENT_PATH))

try:
    from zswe_agent.mcp import MCP_Core
    from zswe_agent.models import TestCase, CodeReview, DevelopmentTask
    from zswe_agent.agents import DeveloperAgent, ReviewerAgent
    from zswe_agent.constitution import ConstitutionGenerator
    from zswe_agent.tools import read_file, write_file, list_directory
    from zswe_agent.llm_api import call_gemini, ModelType
except ImportError as e:
    logging.error(f"Failed to import core agent modules: {e}")
    MCP_Core = None
    TestCase = None
    CodeReview = None
    DevelopmentTask = None
    DeveloperAgent = None
    ReviewerAgent = None
    ConstitutionGenerator = None
    read_file = None
    write_file = None
    list_directory = None
    call_gemini = None
    ModelType = None

logger = logging.getLogger(__name__)

class CoreAgentIntegration:
    """
    Integration layer between the web application and ZSCE Agent core system.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.core_available = MCP_Core is not None
        
        if self.core_available:
            try:
                self.mcp_core = MCP_Core(str(self.project_root))
                self.developer = DeveloperAgent(str(self.project_root))
                self.reviewer = ReviewerAgent()
                self.constitution_generator = ConstitutionGenerator(str(self.project_root))
                logger.info("Core agent integration initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize core agent: {e}")
                self.core_available = False
        else:
            logger.warning("Core agent modules not available")
    
    def is_available(self) -> bool:
        """Check if core agent integration is available."""
        return self.core_available
    
    async def run_workflow_async(self, user_prompt: str, auto_approve: bool = True) -> Dict[str, Any]:
        """
        Run the core agent workflow asynchronously.
        
        Args:
            user_prompt: The development task for the agent to perform
            auto_approve: Whether to auto-approve all prompts
            
        Returns:
            Dictionary containing workflow results
        """
        if not self.core_available:
            return {
                "success": False,
                "error": "Core agent not available",
                "workflow_id": None
            }
        
        try:
            # Generate workflow ID
            workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Run workflow in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._run_workflow_sync, 
                user_prompt, 
                auto_approve, 
                workflow_id
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": None
            }
    
    def _run_workflow_sync(self, user_prompt: str, auto_approve: bool, workflow_id: str) -> Dict[str, Any]:
        """
        Synchronous workflow execution (runs in executor thread).
        """
        try:
            # Generate project constitution
            constitution = self.constitution_generator.generate()
            
            # Step 1: Reviewer writes a failing test
            logger.info("Step 1: Reviewer writing failing test")
            test_code_str = self.reviewer.write_test(user_prompt, constitution)
            
            # Generate file paths
            test_file_path, impl_file_path = self._generate_file_paths(user_prompt)
            test_case = TestCase(file_path=test_file_path, code=test_code_str)
            
            # Step 2: Developer writes initial code
            logger.info("Step 2: Developer writing initial code")
            dev_context = self._build_developer_context(user_prompt, test_case, constitution)
            current_code = self.developer.execute_task(dev_context)
            
            # Step 3: Debate loop
            debate_rounds = []
            final_review = None
            
            for i in range(3):  # MAX_DEBATE_ROUNDS
                logger.info(f"Debate round {i + 1}/3")
                review_str = self.reviewer.review_code(current_code, constitution)
                
                debate_rounds.append({
                    "round": i + 1,
                    "review": review_str,
                    "code": current_code
                })
                
                if "LGTM" in review_str.upper():
                    logger.info("Code approved by Reviewer Agent")
                    final_review = review_str
                    break
                
                # Developer fixes the code
                current_code = self.developer.fix_code(critique=review_str, original_code=current_code)
                final_review = review_str
            
            # Prepare result
            result = {
                "success": True,
                "workflow_id": workflow_id,
                "user_prompt": user_prompt,
                "constitution": constitution,
                "test_case": {
                    "file_path": test_case.file_path,
                    "code": test_case.code
                },
                "implementation": {
                    "file_path": impl_file_path,
                    "code": current_code
                },
                "debate_rounds": debate_rounds,
                "final_review": final_review,
                "approved": "LGTM" in (final_review or "").upper(),
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    def _generate_file_paths(self, user_prompt: str) -> tuple[str, str]:
        """Generate dynamic file paths based on user prompt."""
        words = user_prompt.lower().split()
        stop_words = {'create', 'make', 'build', 'implement', 'add', 'write', 'a', 'an', 'the', 'that', 'this', 'is', 'are', 'was', 'were', 'will', 'can', 'should', 'would', 'could'}
        meaningful_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        if meaningful_words:
            feature_name = meaningful_words[0]
        else:
            feature_name = "new_feature"
        
        test_file_path = f"tests/test_{feature_name}.py"
        impl_file_path = f"zswe_agent/{feature_name}.py"
        
        return test_file_path, impl_file_path
    
    def _build_developer_context(self, user_prompt: str, test_case: TestCase, constitution: str) -> str:
        """Build context for developer agent."""
        context = f"""{constitution}

User Requirement: {user_prompt}

Failing Test Case (`{test_case.file_path}`):
```python
{test_case.code}
```

Please write the implementation code that makes the above test case pass."""
        return context
    
    def get_project_constitution(self) -> Dict[str, Any]:
        """Get the current project constitution."""
        if not self.core_available:
            return {
                "success": False,
                "error": "Core agent not available"
            }
        
        try:
            constitution = self.constitution_generator.generate()
            return {
                "success": True,
                "constitution": constitution,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to generate constitution: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_project_files(self) -> Dict[str, Any]:
        """List files in the project directory."""
        if not self.core_available:
            return {
                "success": False,
                "error": "Core agent not available"
            }
        
        try:
            files = list_directory(str(self.project_root))
            return {
                "success": True,
                "files": files,
                "project_root": str(self.project_root),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to list project files: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def read_project_file(self, file_path: str) -> Dict[str, Any]:
        """Read a file from the project directory."""
        if not self.core_available:
            return {
                "success": False,
                "error": "Core agent not available"
            }
        
        try:
            full_path = self.project_root / file_path
            if not full_path.exists():
                return {
                    "success": False,
                    "error": "File not found"
                }
            
            content = read_file(str(full_path))
            return {
                "success": True,
                "file_path": file_path,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def write_project_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write a file to the project directory."""
        if not self.core_available:
            return {
                "success": False,
                "error": "Core agent not available"
            }
        
        try:
            full_path = self.project_root / file_path
            # Ensure directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            write_file(str(full_path), content)
            return {
                "success": True,
                "file_path": file_path,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
core_integration = CoreAgentIntegration()

# Convenience functions for API endpoints
async def run_agent_workflow(user_prompt: str, auto_approve: bool = True) -> Dict[str, Any]:
    """Run agent workflow with given prompt."""
    return await core_integration.run_workflow_async(user_prompt, auto_approve)

async def get_constitution() -> Dict[str, Any]:
    """Get project constitution."""
    return core_integration.get_project_constitution()

async def list_files() -> Dict[str, Any]:
    """List project files."""
    return core_integration.list_project_files()

async def read_file_content(file_path: str) -> Dict[str, Any]:
    """Read file content."""
    return core_integration.read_project_file(file_path)

async def write_file_content(file_path: str, content: str) -> Dict[str, Any]:
    """Write file content."""
    return core_integration.write_project_file(file_path, content)
