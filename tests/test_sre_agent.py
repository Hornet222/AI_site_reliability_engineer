import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from src.agents.sre_agent import (
    get_recent_commits,
    get_security_alerts,
    analyze_file_changes,
    generate_sre_insight
)
from src.models import CodeChange, SecurityAlert, SREInsight

# Mock data
MOCK_COMMIT = {
    "sha": "abc123def456",
    "commit": {
        "author": {
            "name": "Test User",
            "email": "test@example.com",
            "date": "2024-03-14T12:00:00Z"
        },
        "message": "Update authentication system"
    },
    "files": [
        {"filename": "auth/login.py"},
        {"filename": "auth/middleware.py"}
    ]
}

MOCK_CODE_ALERT = {
    "number": 42,
    "state": "open",
    "rule": {
        "severity": "high",
        "description": "SQL Injection vulnerability detected"
    }
}

MOCK_SECRET_ALERT = {
    "number": 43,
    "state": "open",
    "secret_type": "AWS Access Key",
    "resolution": None
}

@pytest.fixture
def mock_context():
    """Create a mock RunContext with GitHub MCP server."""
    ctx = MagicMock()
    ctx.mcp = MagicMock()
    ctx.mcp.github = MagicMock()
    return ctx

@pytest.mark.asyncio
async def test_get_recent_commits(mock_context):
    """Test fetching recent commits."""
    # Setup mock
    mock_context.mcp.github.list_commits = AsyncMock(return_value=[MOCK_COMMIT])
    
    # Execute
    result = await get_recent_commits(mock_context, "owner", "repo", 7)
    
    # Assert
    assert len(result) == 1
    assert result[0]["sha"] == "abc123def456"
    mock_context.mcp.github.list_commits.assert_called_once()

@pytest.mark.asyncio
async def test_get_security_alerts(mock_context):
    """Test fetching security alerts."""
    # Setup mocks
    mock_context.mcp.github.list_code_scanning_alerts = AsyncMock(return_value=[MOCK_CODE_ALERT])
    mock_context.mcp.github.list_secret_scanning_alerts = AsyncMock(return_value=[MOCK_SECRET_ALERT])
    
    # Execute
    result = await get_security_alerts(mock_context, "owner", "repo")
    
    # Assert
    assert len(result["code_scanning"]) == 1
    assert len(result["secret_scanning"]) == 1
    assert result["code_scanning"][0]["number"] == 42
    assert result["secret_scanning"][0]["number"] == 43

@pytest.mark.asyncio
async def test_analyze_file_changes(mock_context):
    """Test analyzing file changes in a commit."""
    # Setup mock
    mock_context.mcp.github.get_commit = AsyncMock(return_value=MOCK_COMMIT)
    
    # Execute
    result = await analyze_file_changes(mock_context, "owner", "repo", "abc123")
    
    # Assert
    assert result["sha"] == "abc123def456"
    assert len(result["files"]) == 2
    mock_context.mcp.github.get_commit.assert_called_once()

@pytest.mark.asyncio
async def test_generate_sre_insight():
    """Test generating complete SRE insight."""
    mock_insight = SREInsight(
        repository="owner/repo",
        code_changes=[
            CodeChange(
                commit_sha="abc123",
                author="test@example.com",
                message="Update auth",
                date="2024-03-14T12:00:00Z",
                files_changed=["auth/login.py"],
                impact_score=0.8
            )
        ],
        security_alerts=[
            SecurityAlert(
                alert_number=42,
                severity="high",
                state="open",
                description="SQL Injection vulnerability",
                affected_files=["auth/login.py"]
            )
        ],
        risk_assessment="High risk due to authentication changes",
        recommendations=["Review SQL queries", "Add input validation"]
    )
    
    # Mock the agent's run method
    with patch('src.agents.sre_agent.sre_agent.run', new_callable=AsyncMock) as mock_run:
        mock_run.return_value.data = mock_insight
        
        # Execute
        result = await generate_sre_insight("owner", "repo")
        
        # Assert
        assert isinstance(result, SREInsight)
        assert result.repository == "owner/repo"
        assert len(result.code_changes) == 1
        assert len(result.security_alerts) == 1
        assert result.code_changes[0].impact_score == 0.8
        assert "SQL Injection" in result.security_alerts[0].description

@pytest.mark.asyncio
async def test_error_handling(mock_context):
    """Test error handling in tools."""
    # Setup mock to raise exception
    mock_context.mcp.github.list_commits = AsyncMock(side_effect=Exception("API Error"))
    
    # Execute and assert
    result = await get_recent_commits(mock_context, "owner", "repo")
    assert result == []  # Should return empty list on error

@pytest.mark.asyncio
async def test_model_validation():
    """Test Pydantic model validation."""
    # Test invalid impact score
    with pytest.raises(ValueError):
        CodeChange(
            commit_sha="abc123",
            author="test@example.com",
            message="test",
            date="2024-03-14",
            impact_score=1.5  # Invalid: should be between 0 and 1
        )
    
    # Test valid model
    alert = SecurityAlert(
        alert_number=1,
        severity="medium",
        state="open",
        description="test alert"
    )
    assert alert.affected_files == []  # Should use default empty list 