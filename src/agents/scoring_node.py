from src.entity.state import CreditAgentState
from src.tools.credit_api_client import score_credit_risk
from src.logging.logger import logging

def scoring_node(state: CreditAgentState) -> dict:
    """
    Retrieves the extracted financial features from the state and sends them
    to the deterministic Credit Risk API to generate a default prediction.
    """
    logging.info("Executing scoring_node: Fetching risk scores from API.")
    
    payload = state.get("extracted_features")
    if not payload:
        logging.error("scoring_node failed: 'extracted_features' is missing or empty.")
        raise ValueError("State is missing 'extracted_features'. Cannot compute risk score.")
        
    try:
        api_response = score_credit_risk(payload)

        risk_prediction = api_response.get("predicted_default")
        risk_probability = api_response.get("default_probability")
        
        logging.info(f"Scoring complete. Prediction: {risk_prediction}, Probability: {risk_probability}")

        return {
            "risk_prediction": risk_prediction,
            "risk_probability": risk_probability
        }
        
    except Exception as e:
        logging.error(f"Failed to fetch credit score in scoring_node: {e}")
        raise e