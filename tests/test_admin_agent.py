import pytest
from unittest.mock import MagicMock, patch
from core.admin_agent import AdminAgent


@pytest.fixture
def agent():
    """Creates a fresh AdminAgent for each test."""
    return AdminAgent()


def test_format_request_message(agent):
    """Tests that the LLM formats the request message correctly."""
    with patch.object(agent.llm, "invoke", return_value=MagicMock(content="Mocked admin message")):
        message = agent._format_request_message("Alice", "XYZ-987", "1 Day")
        assert "Mocked admin message" in str(message)


@patch("core.admin_agent.requests.post")
def test_escalate_reservation_success(mock_post, agent):
    """Tests that a request is correctly sent to the Admin API."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    with patch.object(agent, "_format_request_message", return_value="Mocked message"):
        req_id = agent.escalate_reservation("Bob", "LMN-456", "3 Hours")

    assert req_id is not None
    assert req_id.startswith("REQ-")


@patch("core.admin_agent.requests.post")
def test_escalate_reservation_api_failure(mock_post, agent):
    """Tests graceful failure when the Admin API is unreachable."""
    from requests.exceptions import ConnectionError
    mock_post.side_effect = ConnectionError("API down")

    with patch.object(agent, "_format_request_message", return_value="Mocked"):
        req_id = agent.escalate_reservation("Bob", "LMN-456", "3 Hours")

    assert req_id is None


@patch("core.admin_agent.requests.get")
def test_get_approval_status(mock_get, agent):
    """Tests that status retrieval works."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"status": "APPROVED"}
    mock_get.return_value = mock_response

    status = agent.get_approval_status("REQ-001")
    assert status == "APPROVED"
