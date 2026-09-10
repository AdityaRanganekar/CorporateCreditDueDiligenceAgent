from src.entity.state import CreditAgentState
from src.logging.logger import logging

def route_after_scoring(state: CreditAgentState) -> str:
    """
    Evaluates the risk scores from the state to determine the next execution node.
    Routes to the synthesizer for standard processing, or to human review if thresholds are breached.
    """
    probability = state.get("risk_probability")
    
    if probability is None:
        logging.error("Routing failed: 'risk_probability' is missing from state.")
        raise ValueError("Missing risk probability for conditional routing.")
        
    logging.info(f"Evaluating conditional route for risk probability: {probability}")

    if probability > 0.40:
        logging.warning("High risk threshold exceeded. Routing to human review.")
        return "human_review_node"
    
    logging.info("Risk within acceptable limits. Routing to synthesizer.")
    return "synthesizer_node"