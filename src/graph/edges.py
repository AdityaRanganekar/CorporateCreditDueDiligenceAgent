from src.entity.state import CreditAgentState
from src.logging.logger import logging

def route_after_scoring(state: CreditAgentState) -> str:
    """
    Evaluates the risk scores from the state to determine the next execution node.
    Routes to the synthesizer for standard processing, or to human review if thresholds are breached.
    """
    prediction = state.get("risk_prediction")
    
    if prediction is None:
        logging.error("Routing failed: 'risk_prediction' is missing from state.")
        raise ValueError("Missing risk prediction for conditional routing.")
        
    logging.info(f"Evaluating conditional route for risk prediction: {prediction}")

    if prediction == 1:
        logging.warning("High risk threshold exceeded. Routing to human review.")
        return "human_review_node"
    
    logging.info("Risk within acceptable limits. Routing to synthesizer.")
    return "synthesizer_node"