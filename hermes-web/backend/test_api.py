#!/usr/bin/env python3
"""
Backend API tests using FastAPI TestClient
Tests core V4.0 endpoints: MemoryNexus, Projects, Workflows, Tools, etc.
"""

import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from models import Base
from models import User, Project, Workflow, Conversation, Message, MemoryChunk, ToolCall

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    """Create test client with test database"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def test_user_token(client):
    """Create test user and return JWT token"""
    # Register test user
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 201
    
    # Login to get token
    response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    return response.json()["access_token"]

class TestHealthEndpoints:
    """Test health and database connectivity"""
    
    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
    
    def test_db_ping(self, client):
        response = client.get("/db/ping")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "version" in data

class TestMemoryNexusEndpoints:
    """Test AgentMemoryNexus CRUD operations"""
    
    def test_create_conversation(self, client, test_user_token):
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.post("/memory/conversations", 
            json={
                "agent_name": "test_agent",
                "purpose": "testing"
            },
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["agent_name"] == "test_agent"
        assert data["purpose"] == "testing"
        return data["id"]
    
    def test_create_message(self, client, test_user_token):
        # First create a conversation
        conv_id = self.test_create_conversation(client, test_user_token)
        
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.post("/memory/messages",
            json={
                "conversation_id": conv_id,
                "sender": "user",
                "content": "Test message",
                "role": "user"
            },
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Test message"
        assert data["sender"] == "user"
        return data["id"]
    
    def test_create_memory_chunk(self, client, test_user_token):
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.post("/memory/chunks",
            json={
                "source_type": "conversation",
                "source_id": "test_conv",
                "content": "Test memory chunk content",
                "metadata_json": {"test": "data"}
            },
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Test memory chunk content"
        assert data["source_type"] == "conversation"
        return data["id"]
    
    def test_search_memory_chunks(self, client, test_user_token):
        # Create a memory chunk first
        chunk_id = self.test_create_memory_chunk(client, test_user_token)
        
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.post("/memory/chunks/search",
            json={
                "query_text": "memory chunk",
                "top_k": 5
            },
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should find our test chunk
        assert len(data) >= 1

class TestProjectEndpoints:
    """Test Project CRUD operations"""
    
    def test_create_project(self, client, test_user_token):
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.post("/projects",
            json={
                "name": "Test Project",
                "description": "A test project for API testing"
            },
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["description"] == "A test project for API testing"
        return data["id"]
    
    def test_get_projects(self, client, test_user_token):
        # Create a project first
        self.test_create_project(client, test_user_token)
        
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.get("/projects", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_project_detail(self, client, test_user_token):
        # Create a project first
        project_id = self.test_create_project(client, test_user_token)
        
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.get(f"/projects/{project_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert data["name"] == "Test Project"

class TestWorkflowEndpoints:
    """Test Workflow CRUD operations"""
    
    def test_create_workflow(self, client, test_user_token):
        # Create a project first
        project_id = TestProjectEndpoints().test_create_project(client, test_user_token)
        
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.post("/workflows",
            json={
                "project_id": project_id,
                "task_description": "Test workflow task",
                "status": "pending"
            },
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["project_id"] == project_id
        assert data["task_description"] == "Test workflow task"
        return data["id"]
    
    def test_get_workflows(self, client, test_user_token):
        # Create a workflow first
        self.test_create_workflow(client, test_user_token)
        
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.get("/workflows", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_workflow_detail(self, client, test_user_token):
        # Create a workflow first
        workflow_id = self.test_create_workflow(client, test_user_token)
        
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.get(f"/workflows/{workflow_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == workflow_id

class TestToolEndpoints:
    """Test Tool Selection Module endpoints"""
    
    def test_register_tool(self, client, test_user_token):
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.post("/tools/register",
            json={
                "tool_name": "test_tool",
                "description": "A test tool for API testing",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string"}
                    },
                    "required": ["input"]
                }
            },
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "test_tool" in data["message"]
    
    def test_list_tools(self, client, test_user_token):
        # Register a tool first
        self.test_register_tool(client, test_user_token)
        
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.get("/tools", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["tool_name"] == "test_tool"
    
    def test_execute_tool(self, client, test_user_token):
        # Register a tool first
        self.test_register_tool(client, test_user_token)
        
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.post("/tools/execute",
            json={
                "tool_name": "test_tool",
                "input": {"input": "test data"}
            },
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["tool_name"] == "test_tool"
        assert "output" in data
        assert "audited_call_id" in data

class TestConstitutionalGovernance:
    """Test constitutional governance checks"""
    
    def test_meditation_framework(self, client, test_user_token):
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.post("/meditation/frame",
            json={
                "user_prompt": "Test problem framing",
                "context": "Test context"
            },
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "problem_statement" in data
        assert "key_entities" in data
        assert "constraints" in data
        assert "success_metrics" in data
    
    def test_debate_engine(self, client, test_user_token):
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.post("/debate/one-on-one",
            json={
                "topic": "Test debate topic",
                "context": "Test context"
            },
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "transcript" in data
        assert "verdict" in data
        assert isinstance(data["transcript"], list)

class TestKnowledgeGraphEndpoints:
    """Test Knowledge Graph CRUD operations"""
    
    def test_create_kg_node(self, client, test_user_token):
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.post("/kg/nodes",
            json={
                "entity_type": "concept",
                "properties": {"name": "test_concept", "description": "A test concept"}
            },
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["entity_type"] == "concept"
        assert data["properties"]["name"] == "test_concept"
        return data["id"]
    
    def test_create_kg_edge(self, client, test_user_token):
        # Create two nodes first
        node1_id = self.test_create_kg_node(client, test_user_token)
        node2_id = self.test_create_kg_node(client, test_user_token)
        
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.post("/kg/edges",
            json={
                "source_node_id": node1_id,
                "target_node_id": node2_id,
                "relationship_type": "related_to",
                "properties": {"strength": 0.8}
            },
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["source_node_id"] == node1_id
        assert data["target_node_id"] == node2_id
        assert data["relationship_type"] == "related_to"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
