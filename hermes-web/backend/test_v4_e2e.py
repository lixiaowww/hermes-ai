"""
V4.0核心流程端到端测试

测试MeditationModule -> DebateEngine -> HighDimensionModule的完整工作流
"""

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestV4E2E:
    """V4.0核心流程端到端测试"""
    
    def test_meditation_to_debate_workflow(self):
        """测试问题框架化到辩论的完整工作流"""
        
        # Step 1: 问题框架化
        meditation_request = {
            "prompt": "优化数据库查询性能，特别是用户表的复杂查询",
            "context": {
                "project_type": "web_application",
                "tech_stack": ["Python", "PostgreSQL", "FastAPI"],
                "current_issues": ["慢查询", "索引缺失", "N+1问题"]
            }
        }
        
        response = client.post("/meditation/frame", json=meditation_request)
        assert response.status_code == 200
        
        meditation_result = response.json()
        assert meditation_result["success"] == True
        assert "insight_report" in meditation_result
        assert "entities" in meditation_result["insight_report"]
        assert "constraints" in meditation_result["insight_report"]
        assert "objectives" in meditation_result["insight_report"]
        
        # Step 2: 发起辩论
        debate_request = {
            "topic": "数据库查询优化策略",
            "participants": ["performance_expert", "database_admin", "backend_developer"],
            "context": meditation_result["insight_report"]
        }
        
        response = client.post("/debate/initiate", json=debate_request)
        assert response.status_code == 200
        
        debate_result = response.json()
        assert debate_result["success"] == True
        debate_id = debate_result["debate_id"]
        
        # Step 3: 添加论证
        arguments = [
            {
                "agent_id": "performance_expert",
                "argument_type": "evidence",
                "content": "根据性能分析，用户表的查询响应时间平均为2.5秒，超过可接受阈值"
            },
            {
                "agent_id": "database_admin",
                "argument_type": "reasoning",
                "content": "建议添加复合索引来优化多条件查询"
            },
            {
                "agent_id": "backend_developer",
                "argument_type": "rebuttal",
                "content": "索引会增加写入开销，需要权衡读写性能"
            }
        ]
        
        for arg in arguments:
            response = client.post(f"/debate/{debate_id}/argument", json=arg)
            assert response.status_code == 200
        
        # Step 4: 检查辩论状态
        response = client.get(f"/debate/{debate_id}/status")
        assert response.status_code == 200
        
        status_result = response.json()
        assert status_result["status"] in ["active", "concluded"]
        assert status_result["rounds"] >= 1
        
        # Step 5: 获取辩论轮次
        response = client.get(f"/debate/{debate_id}/rounds")
        assert response.status_code == 200
        
        rounds_result = response.json()
        assert len(rounds_result["rounds"]) >= 1
        
        return {
            "meditation_result": meditation_result,
            "debate_id": debate_id,
            "debate_status": status_result,
            "debate_rounds": rounds_result
        }
    
    def test_code_analysis_to_impact_workflow(self):
        """测试代码分析到影响评估的完整工作流"""
        
        # Step 1: 代码分析
        analysis_request = {
            "target_paths": ["main.py", "models.py"],
            "analysis_depth": "comprehensive",
            "include_dependencies": True
        }
        
        response = client.post("/high-dimension/analyze", json=analysis_request)
        assert response.status_code == 200
        
        analysis_result = response.json()
        assert analysis_result["success"] == True
        assert "analysis_result" in analysis_result
        assert "total_entities" in analysis_result["analysis_result"]
        assert "dependencies" in analysis_result["analysis_result"]
        
        # Step 2: 影响分析
        impact_request = {
            "target_entity": "main.py",
            "change_type": "modification",
            "change_description": "添加新的API端点"
        }
        
        response = client.post("/high-dimension/impact", json=impact_request)
        assert response.status_code == 200
        
        impact_result = response.json()
        assert impact_result["success"] == True
        assert "impact_report" in impact_result
        assert "affected_entities" in impact_result["impact_report"]
        assert "risk_assessment" in impact_result["impact_report"]
        
        return {
            "analysis_result": analysis_result,
            "impact_result": impact_result
        }
    
    def test_full_v4_workflow(self):
        """测试完整的V4.0工作流"""
        
        # 1. 问题框架化
        meditation_result = self.test_meditation_to_debate_workflow()
        
        # 2. 代码分析
        analysis_result = self.test_code_analysis_to_impact_workflow()
        
        # 3. 验证工作流完整性
        assert meditation_result["meditation_result"]["success"] == True
        assert analysis_result["analysis_result"]["success"] == True
        
        # 4. 验证数据一致性
        meditation_entities = meditation_result["meditation_result"]["core_insights"]["entities"]
        analysis_entities = analysis_result["analysis_result"]["analysis_result"]["entities"]
        
        # 验证实体识别的一致性
        assert len(meditation_entities) > 0
        assert len(analysis_entities) > 0
        
        return {
            "meditation": meditation_result,
            "analysis": analysis_result,
            "workflow_complete": True
        }
    
    def test_error_handling_workflow(self):
        """测试错误处理工作流"""
        
        # 测试无效的meditation请求
        invalid_request = {
            "prompt": "",  # 空提示
            "context": {}
        }
        
        response = client.post("/meditation/frame", json=invalid_request)
        assert response.status_code == 422  # 验证错误
        
        # 测试无效的debate请求
        invalid_debate = {
            "topic": "",
            "participants": [],
            "context": {}
        }
        
        response = client.post("/debate/initiate", json=invalid_debate)
        assert response.status_code == 422
        
        # 测试无效的分析请求
        invalid_analysis = {
            "target_paths": [],
            "analysis_depth": "invalid_depth"
        }
        
        response = client.post("/high-dimension/analyze", json=invalid_analysis)
        assert response.status_code == 422
    
    def test_performance_workflow(self):
        """测试性能工作流"""
        import time
        
        # 测试meditation性能
        start_time = time.time()
        meditation_request = {
            "prompt": "实现用户认证系统",
            "context": {"project_type": "web_application"}
        }
        response = client.post("/meditation/frame", json=meditation_request)
        meditation_time = time.time() - start_time
        
        assert response.status_code == 200
        assert meditation_time < 5.0  # 应该在5秒内完成
        
        # 测试debate性能
        start_time = time.time()
        debate_request = {
            "topic": "用户认证策略",
            "participants": ["security_expert", "backend_developer"],
            "context": {"security_requirements": "high"}
        }
        response = client.post("/debate/initiate", json=debate_request)
        debate_time = time.time() - start_time
        
        assert response.status_code == 200
        assert debate_time < 3.0  # 应该在3秒内完成
        
        # 测试analysis性能
        start_time = time.time()
        analysis_request = {
            "target_paths": ["main.py"],
            "analysis_depth": "basic"
        }
        response = client.post("/high-dimension/analyze", json=analysis_request)
        analysis_time = time.time() - start_time
        
        assert response.status_code == 200
        assert analysis_time < 2.0  # 应该在2秒内完成
        
        return {
            "meditation_time": meditation_time,
            "debate_time": debate_time,
            "analysis_time": analysis_time,
            "total_time": meditation_time + debate_time + analysis_time
        }
    
    def test_concurrent_workflows(self):
        """测试并发工作流"""
        import threading
        import time
        
        results = []
        errors = []
        
        def run_workflow(workflow_id):
            try:
                # 模拟并发工作流
                meditation_request = {
                    "prompt": f"实现功能{workflow_id}",
                    "context": {"workflow_id": workflow_id}
                }
                
                response = client.post("/meditation/frame", json=meditation_request)
                if response.status_code == 200:
                    results.append(workflow_id)
                else:
                    errors.append(f"Workflow {workflow_id} failed: {response.status_code}")
                    
            except Exception as e:
                errors.append(f"Workflow {workflow_id} error: {str(e)}")
        
        # 启动5个并发工作流
        threads = []
        for i in range(5):
            thread = threading.Thread(target=run_workflow, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        assert len(results) == 5, f"Expected 5 successful workflows, got {len(results)}"
        assert len(errors) == 0, f"Expected no errors, got {errors}"
        
        return {
            "successful_workflows": len(results),
            "errors": errors,
            "concurrent_test_passed": True
        }

# 性能基准测试
def test_v4_performance_benchmarks():
    """V4.0性能基准测试"""
    
    test_e2e = TestV4E2E()
    
    # 运行性能测试
    performance_result = test_e2e.test_performance_workflow()
    
    # 验证性能指标
    assert performance_result["meditation_time"] < 5.0
    assert performance_result["debate_time"] < 3.0
    assert performance_result["analysis_time"] < 2.0
    assert performance_result["total_time"] < 10.0
    
    print(f"Performance Results:")
    print(f"  Meditation: {performance_result['meditation_time']:.2f}s")
    print(f"  Debate: {performance_result['debate_time']:.2f}s")
    print(f"  Analysis: {performance_result['analysis_time']:.2f}s")
    print(f"  Total: {performance_result['total_time']:.2f}s")

# 集成测试
def test_v4_integration():
    """V4.0集成测试"""
    
    test_e2e = TestV4E2E()
    
    # 运行完整工作流
    workflow_result = test_e2e.test_full_v4_workflow()
    
    # 验证集成结果
    assert workflow_result["workflow_complete"] == True
    assert workflow_result["meditation"]["meditation_result"]["success"] == True
    assert workflow_result["analysis"]["analysis_result"]["success"] == True
    
    print("V4.0 Integration Test Passed!")
    print(f"  Meditation Success: {workflow_result['meditation']['meditation_result']['success']}")
    print(f"  Analysis Success: {workflow_result['analysis']['analysis_result']['success']}")
    print(f"  Workflow Complete: {workflow_result['workflow_complete']}")

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
