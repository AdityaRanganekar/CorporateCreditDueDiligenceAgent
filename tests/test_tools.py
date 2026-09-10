import pytest
import httpx
from unittest.mock import patch, Mock
from src.tools.credit_api_client import score_credit_risk

MOCK_PAYLOAD = {
    "loan_amnt": 15000.0, 
    "term": " 36 months", 
    "int_rate": 12.5,
    "installment": 450.0, 
    "grade": "B", 
    "sub_grade": "B2",
    "emp_length": "5 years", 
    "home_ownership": "MORTGAGE",
    "annual_inc": 85000.0, 
    "verification_status": "Verified",
    "purpose": "debt consolidation", 
    "addr_state": "NY", 
    "dti": 18.5,
    "open_acc": 12.0, 
    "pub_rec": 0.0, 
    "revol_bal": 12400.0,
    "revol_util": 45.2, 
    "total_acc": 22.0, 
    "mort_acc": 2.0,
    "pub_rec_bankruptcies": 0.0
}

@patch("src.tools.credit_api_client.httpx.post")
def test_score_credit_risk_success(mock_post):
    """Test that the tool correctly parses a successful API response."""

    mock_response = Mock()
    mock_response.json.return_value = {"predicted_default": 0, "default_probability": 0.12}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    result = score_credit_risk(MOCK_PAYLOAD)

    assert result["predicted_default"] == 0
    assert result["default_probability"] == 0.12
    mock_post.assert_called_once()

@patch("src.tools.credit_api_client.httpx.post")
def test_score_credit_risk_max_retries_failure(mock_post):
    """Test that the tool throws a ConnectionError after exhausting retries."""
    mock_post.side_effect = httpx.TimeoutException("Mocked timeout")

    with pytest.raises(ConnectionError, match="Failed to fetch risk score"):
        score_credit_risk(MOCK_PAYLOAD, max_retries=1)