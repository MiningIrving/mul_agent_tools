"""
Basic tests for the multi-agent financial analysis framework.
"""

import pytest
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.state import GraphState, TaskDefinition, ErrorRecord
from agents.base import BaseAgent
from tools.base import BaseTool


class TestGraphState:
    """Test GraphState functionality."""
    
    def test_state_initialization(self):
        """Test GraphState initialization."""
        state = GraphState(
            original_query="Test query",
            session_id="test_session"
        )
        
        assert state.original_query == "Test query"
        assert state.session_id == "test_session"
        assert state.query_complexity is None
        assert len(state.task_plan) == 0
        assert len(state.agent_results) == 0
        assert len(state.error_log) == 0
        assert state.final_answer == ""
    
    def test_add_error(self):
        """Test adding error records."""
        state = GraphState(
            original_query="Test query",
            session_id="test_session"
        )
        
        state.add_error(
            task_id="test_task",
            agent="test_agent",
            tool="test_tool",
            error_type="TEST_ERROR",
            error_message="Test error message"
        )
        
        assert len(state.error_log) == 1
        error = state.error_log[0]
        assert error.task_id == "test_task"
        assert error.agent == "test_agent"
        assert error.error_type == "TEST_ERROR"
    
    def test_task_management(self):
        """Test task management methods."""
        state = GraphState(
            original_query="Test query",
            session_id="test_session"
        )
        
        # Add a task
        task = TaskDefinition(
            task_id="test_task",
            agent="test_agent",
            tool="test_tool",
            inputs={"param": "value"}
        )
        state.task_plan = [task]
        
        # Test getting task by ID
        retrieved_task = state.get_task_by_id("test_task")
        assert retrieved_task is not None
        assert retrieved_task.task_id == "test_task"
        
        # Test getting pending tasks
        pending = state.get_pending_tasks()
        assert len(pending) == 1
        
        # Test marking task as completed
        state.mark_task_completed("test_task", {"result": "success"})
        assert task.status == "completed"
        assert "test_task" in state.agent_results
        
        # Test no more pending tasks
        pending = state.get_pending_tasks()
        assert len(pending) == 0


class TestTaskDefinition:
    """Test TaskDefinition functionality."""
    
    def test_task_creation(self):
        """Test task creation."""
        task = TaskDefinition(
            task_id="test_task",
            agent="test_agent", 
            tool="test_tool",
            inputs={"param": "value"}
        )
        
        assert task.task_id == "test_task"
        assert task.agent == "test_agent"
        assert task.tool == "test_tool"
        assert task.inputs == {"param": "value"}
        assert task.status == "pending"
        assert task.depends_on is None


class TestErrorRecord:
    """Test ErrorRecord functionality."""
    
    def test_error_creation(self):
        """Test error record creation."""
        error = ErrorRecord(
            task_id="test_task",
            agent="test_agent",
            tool="test_tool", 
            error_type="TEST_ERROR",
            error_message="Test error"
        )
        
        assert error.task_id == "test_task"
        assert error.agent == "test_agent"
        assert error.tool == "test_tool"
        assert error.error_type == "TEST_ERROR"
        assert error.error_message == "Test error"
        assert error.retry_count == 0
        assert isinstance(error.timestamp, datetime)


class MockAgent(BaseAgent):
    """Mock agent for testing."""
    
    def execute_task(self, state, task):
        return {"mock_result": "success"}
    
    def get_available_tools(self):
        return ["mock_tool"]


class MockTool(BaseTool):
    """Mock tool for testing."""
    
    def execute(self, **kwargs):
        return {"mock_data": "test"}
    
    def get_schema(self):
        return {
            "type": "object",
            "properties": {
                "test_param": {"type": "string"}
            }
        }
    
    def get_description(self):
        return "Mock tool for testing"


class TestBaseAgent:
    """Test BaseAgent functionality."""
    
    def test_agent_creation(self):
        """Test agent creation."""
        agent = MockAgent("test_agent")
        assert agent.name == "test_agent"
        assert agent.get_available_tools() == ["mock_tool"]
    
    def test_task_validation(self):
        """Test task validation."""
        agent = MockAgent("test_agent")
        
        # Valid task
        valid_task = TaskDefinition(
            task_id="test_task",
            agent="test_agent",
            tool="mock_tool",
            inputs={}
        )
        assert agent.validate_task(valid_task) is True
        
        # Invalid task (wrong tool)
        invalid_task = TaskDefinition(
            task_id="test_task",
            agent="test_agent", 
            tool="invalid_tool",
            inputs={}
        )
        assert agent.validate_task(invalid_task) is False


class TestBaseTool:
    """Test BaseTool functionality."""
    
    def test_tool_creation(self):
        """Test tool creation."""
        tool = MockTool("test_tool")
        assert tool.name == "test_tool"
        assert tool.get_description() == "Mock tool for testing"
    
    def test_tool_execution(self):
        """Test tool execution."""
        tool = MockTool("test_tool")
        result = tool.execute(test_param="value")
        assert result == {"mock_data": "test"}
    
    def test_input_validation(self):
        """Test input validation."""
        tool = MockTool("test_tool")
        
        # This tool doesn't have required fields, so any input should be valid
        assert tool.validate_inputs({}) is True
        assert tool.validate_inputs({"test_param": "value"}) is True


if __name__ == "__main__":
    pytest.main([__file__])