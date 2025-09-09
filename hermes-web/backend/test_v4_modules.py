"""
V4.0 Core Modules Test Suite

测试MeditationModule、DebateEngine和HighDimensionModule的功能
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

class TestMeditationModule:
    """测试MeditationModule - 问题框架化模块"""
    
    def test_meditation_frame_basic(self):
        """测试基本的问题框架化功能"""
        response = client.post("/meditation/frame", json={
            "prompt": "Create a web application for project management",
            "context": {"technology": "Python, FastAPI"}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "insight_report" in data
        assert "problem_statement" in data["insight_report"]
        assert "entities" in data["insight_report"]
        assert "confidence_score" in data["insight_report"]
        assert data["processing_time"] > 0
    
    def test_meditation_frame_complex(self):
        """测试复杂的问题框架化功能"""
        response = client.post("/meditation/frame", json={
            "prompt": "Create a microservices architecture for e-commerce with real-time analytics, user authentication, payment processing, and inventory management",
            "context": {
                "technology": "Python, FastAPI, React, PostgreSQL, Redis",
                "requirements": ["scalability", "security", "performance"]
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["insight_report"]["entities"]) > 0
        assert data["insight_report"]["confidence_score"] > 0
    
    def test_meditation_frame_error_handling(self):
        """测试错误处理"""
        response = client.post("/meditation/frame", json={
            "prompt": "",  # 空提示
            "context": {}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True  # 应该能处理空输入

class TestDebateEngine:
    """测试DebateEngine - 结构化辩论引擎"""
    
    def test_debate_initiate(self):
        """测试发起辩论"""
        response = client.post("/debate/initiate", json={
            "topic": "Should we use microservices or monolithic architecture?",
            "participants": ["developer", "architect", "product_manager"],
            "initial_arguments": {
                "developer": "Microservices provide better scalability",
                "architect": "Monolithic is simpler to start with",
                "product_manager": "We need to consider time to market"
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "debate_id" in data
        assert data["debate_id"] is not None
        
        return data["debate_id"]
    
    def test_debate_add_argument(self):
        """测试添加论证"""
        # 先发起辩论
        debate_id = self.test_debate_initiate()
        
        # 添加论证
        response = client.post(f"/debate/{debate_id}/argument", json={
            "agent_id": "developer",
            "content": "Microservices allow independent scaling and deployment",
            "argument_type": "evidence"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "argument_id" in data
        assert data["argument_id"] is not None
    
    def test_debate_status(self):
        """测试辩论状态"""
        debate_id = self.test_debate_initiate()
        
        response = client.get(f"/debate/{debate_id}/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "topic" in data
        assert "participants" in data
        assert "status" in data
        assert data["id"] == debate_id
    
    def test_debate_rounds(self):
        """测试辩论轮次"""
        debate_id = self.test_debate_initiate()
        
        # 添加一些论证
        client.post(f"/debate/{debate_id}/argument", json={
            "agent_id": "developer",
            "content": "Microservices provide better fault isolation",
            "argument_type": "reasoning"
        })
        
        response = client.get(f"/debate/{debate_id}/rounds")
        
        assert response.status_code == 200
        data = response.json()
        assert "rounds" in data
        assert len(data["rounds"]) > 0
    
    def test_debate_list(self):
        """测试辩论列表"""
        # 创建一些辩论
        self.test_debate_initiate()
        
        response = client.get("/debate/list")
        
        assert response.status_code == 200
        data = response.json()
        assert "debates" in data
        assert len(data["debates"]) > 0
    
    def test_debate_error_handling(self):
        """测试错误处理"""
        # 测试不存在的辩论
        response = client.get("/debate/non-existent-id/status")
        assert response.status_code == 404
        
        # 测试无效的论证类型
        debate_id = self.test_debate_initiate()
        response = client.post(f"/debate/{debate_id}/argument", json={
            "agent_id": "developer",
            "content": "Test argument",
            "argument_type": "invalid_type"
        })
        assert response.status_code == 422  # 验证错误

class TestHighDimensionModule:
    """测试HighDimensionModule - 代码分析引擎"""
    
    def test_code_analysis(self):
        """测试代码分析"""
        response = client.post("/high-dimension/analyze", json={
            "target_paths": ["main.py"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "analysis_result" in data
        assert "total_entities" in data["analysis_result"]
        assert "files_analyzed" in data["analysis_result"]
        assert "entities" in data["analysis_result"]
        assert data["analysis_result"]["total_entities"] > 0
    
    def test_code_analysis_no_paths(self):
        """测试无指定路径的代码分析"""
        response = client.post("/high-dimension/analyze", json={})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["analysis_result"]["total_entities"] > 0
    
    def test_impact_analysis(self):
        """测试影响分析"""
        # 先进行代码分析
        response = client.post("/high-dimension/analyze", json={
            "target_paths": ["main.py"]
        })
        assert response.status_code == 200
        
        # 获取一个实体进行影响分析
        analysis_data = response.json()["analysis_result"]
        entities = analysis_data["entities"]
        assert len(entities) > 0
        
        target_entity = entities[0]["name"]
        
        response = client.post("/high-dimension/impact", json={
            "target_entity": target_entity
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "impact_report" in data
        assert "overall_risk_score" in data["impact_report"]
        assert "recommendations" in data["impact_report"]
    
    def test_impact_analysis_invalid_entity(self):
        """测试无效实体的影响分析"""
        response = client.post("/high-dimension/impact", json={
            "target_entity": "non_existent_entity"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "error" in data
        assert "not found" in data["error"].lower()

class TestV4ModulesIntegration:
    """测试V4.0模块集成"""
    
    def test_meditation_to_debate_workflow(self):
        """测试从问题框架化到辩论的完整工作流"""
        # 1. 问题框架化
        meditation_response = client.post("/meditation/frame", json={
            "prompt": "Design a scalable user authentication system",
            "context": {"technology": "Python, FastAPI, JWT"}
        })
        assert meditation_response.status_code == 200
        
        # 2. 发起辩论
        debate_response = client.post("/debate/initiate", json={
            "topic": "Should we use JWT or session-based authentication?",
            "participants": ["security_expert", "developer", "product_manager"]
        })
        assert debate_response.status_code == 200
        debate_id = debate_response.json()["debate_id"]
        
        # 3. 添加基于框架化结果的论证
        debate_response = client.post(f"/debate/{debate_id}/argument", json={
            "agent_id": "security_expert",
            "content": "JWT provides stateless authentication which is better for scalability",
            "argument_type": "evidence"
        })
        assert debate_response.status_code == 200
    
    def test_code_analysis_to_impact_workflow(self):
        """测试从代码分析到影响分析的完整工作流"""
        # 1. 代码分析
        analysis_response = client.post("/high-dimension/analyze", json={
            "target_paths": ["main.py"]
        })
        assert analysis_response.status_code == 200
        
        # 2. 对多个实体进行影响分析
        entities = analysis_response.json()["analysis_result"]["entities"]
        for entity in entities[:3]:  # 测试前3个实体
            impact_response = client.post("/high-dimension/impact", json={
                "target_entity": entity["name"]
            })
            assert impact_response.status_code == 200
            assert impact_response.json()["success"] is True

def test_v4_modules_performance():
    """测试V4.0模块性能"""
    import time
    
    # 测试MeditationModule性能
    start_time = time.time()
    response = client.post("/meditation/frame", json={
        "prompt": "Create a complex microservices architecture",
        "context": {"technology": "Python, FastAPI, React, PostgreSQL"}
    })
    meditation_time = time.time() - start_time
    
    assert response.status_code == 200
    assert meditation_time < 5.0  # 应该在5秒内完成
    
    # 测试DebateEngine性能
    start_time = time.time()
    response = client.post("/debate/initiate", json={
        "topic": "Performance test debate",
        "participants": ["agent1", "agent2"]
    })
    debate_time = time.time() - start_time
    
    assert response.status_code == 200
    assert debate_time < 2.0  # 应该在2秒内完成
    
    # 测试HighDimensionModule性能
    start_time = time.time()
    response = client.post("/high-dimension/analyze", json={
        "target_paths": ["main.py"]
    })
    analysis_time = time.time() - start_time
    
    assert response.status_code == 200
    assert analysis_time < 10.0  # 应该在10秒内完成

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
