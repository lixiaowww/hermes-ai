"""
Comprehensive test suite for ZSCE Agent core integration.

This test suite validates the integration between the web application
and the core ZSCE Agent system.
"""

import pytest
import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Add the backend path to sys.path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from main import app
from core_integration import core_integration

# Set up test environment
os.environ["GOOGLE_API_KEY"] = "test-key"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def mock_core_integration():
    """Mock the core integration for testing."""
    with patch('core_integration.core_integration') as mock:
        mock.is_available.return_value = True
        mock.project_root = Path("/test/project")
        yield mock

class TestCoreIntegration:
    """Test core agent integration functionality."""
    
    def test_core_status_endpoint(self, client):
        """Test the core status endpoint."""
        response = client.get("/core/status")
        assert response.status_code == 200
        data = response.json()
        assert "available" in data
        assert "project_root" in data
    
    def test_core_constitution_endpoint(self, client, mock_core_integration):
        """Test the core constitution endpoint."""
        # Mock the constitution response
        mock_core_integration.get_project_constitution.return_value = {
            "success": True,
            "constitution": "Test constitution content",
            "timestamp": "2024-01-01T00:00:00"
        }
        
        response = client.get("/core/constitution")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "constitution" in data
    
    def test_core_files_endpoint(self, client, mock_core_integration):
        """Test the core files listing endpoint."""
        # Mock the files response
        mock_core_integration.list_project_files.return_value = {
            "success": True,
            "files": ["file1.py", "file2.py"],
            "project_root": "/test/project",
            "timestamp": "2024-01-01T00:00:00"
        }
        
        response = client.get("/core/files")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "files" in data
        assert len(data["files"]) == 2
    
    def test_core_read_file_endpoint(self, client, mock_core_integration):
        """Test the core read file endpoint."""
        # Mock the file read response
        mock_core_integration.read_project_file.return_value = {
            "success": True,
            "file_path": "test.py",
            "content": "print('Hello, World!')",
            "timestamp": "2024-01-01T00:00:00"
        }
        
        response = client.get("/core/files/test.py")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["file_path"] == "test.py"
        assert "print('Hello, World!')" in data["content"]
    
    def test_core_write_file_endpoint(self, client, mock_core_integration):
        """Test the core write file endpoint."""
        # Mock the file write response
        mock_core_integration.write_project_file.return_value = {
            "success": True,
            "file_path": "test.py",
            "timestamp": "2024-01-01T00:00:00"
        }
        
        response = client.post("/core/files/test.py", json={"content": "print('Hello, World!')"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["file_path"] == "test.py"
    
    def test_core_workflow_endpoint(self, client, mock_core_integration):
        """Test the core workflow endpoint."""
        # Mock the workflow response
        mock_workflow_result = {
            "success": True,
            "workflow_id": "workflow_20240101_000000",
            "user_prompt": "Create a simple hello world function",
            "constitution": "Test constitution",
            "test_case": {
                "file_path": "tests/test_hello.py",
                "code": "def test_hello(): assert hello() == 'Hello, World!'"
            },
            "implementation": {
                "file_path": "hello.py",
                "code": "def hello(): return 'Hello, World!'"
            },
            "debate_rounds": [
                {
                    "round": 1,
                    "review": "Code looks good",
                    "code": "def hello(): return 'Hello, World!'"
                }
            ],
            "final_review": "LGTM",
            "approved": True,
            "timestamp": "2024-01-01T00:00:00"
        }
        
        mock_core_integration.run_workflow_async.return_value = mock_workflow_result
        
        response = client.post("/core/workflow", json={
            "prompt": "Create a simple hello world function",
            "auto_approve": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["workflow_id"] == "workflow_20240101_000000"
        assert data["approved"] is True
    
    def test_core_workflow_error_handling(self, client, mock_core_integration):
        """Test core workflow error handling."""
        # Mock an error response
        mock_core_integration.run_workflow_async.return_value = {
            "success": False,
            "error": "Test error message",
            "workflow_id": None
        }
        
        response = client.post("/core/workflow", json={
            "prompt": "Invalid prompt",
            "auto_approve": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    def test_core_integration_unavailable(self, client):
        """Test behavior when core integration is unavailable."""
        with patch('core_integration.core_integration') as mock:
            mock.is_available.return_value = False
            mock.project_root = Path("/test/project")
            
            response = client.get("/core/status")
            assert response.status_code == 200
            data = response.json()
            assert data["available"] is False
    
    def test_core_constitution_error_handling(self, client, mock_core_integration):
        """Test constitution endpoint error handling."""
        # Mock an error response
        mock_core_integration.get_project_constitution.return_value = {
            "success": False,
            "error": "Constitution generation failed"
        }
        
        response = client.get("/core/constitution")
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
    
    def test_core_files_error_handling(self, client, mock_core_integration):
        """Test files endpoint error handling."""
        # Mock an error response
        mock_core_integration.list_project_files.return_value = {
            "success": False,
            "error": "File listing failed"
        }
        
        response = client.get("/core/files")
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

class TestCoreIntegrationReal:
    """Test core integration with real core agent (if available)."""
    
    @pytest.mark.skipif(not core_integration.is_available(), reason="Core agent not available")
    def test_real_core_status(self, client):
        """Test core status with real integration."""
        response = client.get("/core/status")
        assert response.status_code == 200
        data = response.json()
        assert data["available"] is True
    
    @pytest.mark.skipif(not core_integration.is_available(), reason="Core agent not available")
    def test_real_core_constitution(self, client):
        """Test core constitution with real integration."""
        response = client.get("/core/constitution")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "constitution" in data
    
    @pytest.mark.skipif(not core_integration.is_available(), reason="Core agent not available")
    def test_real_core_files(self, client):
        """Test core files with real integration."""
        response = client.get("/core/files")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "files" in data

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
