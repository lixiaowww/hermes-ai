"""
V4.0核心模块简化测试

测试各个模块的基本功能，不涉及复杂的端到端工作流
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestV4Simple:
    """V4.0核心模块简化测试"""
    
    def test_meditation_module_basic(self):
        """测试MeditationModule基本功能"""
        request = {
            "prompt": "实现用户认证系统",
            "context": {"project_type": "web_application"}
        }
        
        response = client.post("/meditation/frame", json=request)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] == True
        assert "insight_report" in result
        assert "processing_time" in result
        
        print(f"MeditationModule测试通过: {result['processing_time']:.3f}s")
    
    def test_debate_engine_basic(self):
        """测试DebateEngine基本功能"""
        # 发起辩论
        request = {
            "topic": "用户认证策略选择",
            "participants": ["security_expert", "backend_developer"],
            "context": {"security_requirements": "high"}
        }
        
        response = client.post("/debate/initiate", json=request)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] == True
        assert "debate_id" in result
        
        debate_id = result["debate_id"]
        print(f"DebateEngine发起辩论成功: {debate_id}")
        
        # 检查辩论状态
        response = client.get(f"/debate/{debate_id}/status")
        assert response.status_code == 200
        
        status = response.json()
        assert "status" in status
        print(f"辩论状态: {status['status']}")
        
        return debate_id
    
    def test_high_dimension_module_basic(self):
        """测试HighDimensionModule基本功能"""
        request = {
            "target_paths": ["main.py"],
            "analysis_depth": "basic"
        }
        
        response = client.post("/high-dimension/analyze", json=request)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] == True
        assert "analysis_result" in result
        assert "total_entities" in result["analysis_result"]
        
        print(f"HighDimensionModule测试通过: 发现{result['analysis_result']['total_entities']}个实体")
    
    def test_all_modules_working(self):
        """测试所有模块都在工作"""
        # 测试MeditationModule
        meditation_result = self.test_meditation_module_basic()
        
        # 测试DebateEngine
        debate_id = self.test_debate_engine_basic()
        
        # 测试HighDimensionModule
        analysis_result = self.test_high_dimension_module_basic()
        
        print("所有V4.0核心模块测试通过!")
        return {
            "meditation": meditation_result,
            "debate_id": debate_id,
            "analysis": analysis_result
        }

if __name__ == "__main__":
    # 运行测试
    test = TestV4Simple()
    test.test_all_modules_working()
