from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.entity.state import CreditAgentState
from src.agents.extractor_node import extractor_node
from src.agents.scoring_node import scoring_node
from src.agents.synthesizer_node import synthesizer_node
from src.graph.edges import route_after_scoring
from src.logging.logger import logging

def human_review_node(state: CreditAgentState) -> dict:
    """
    A placeholder node designed to act as an interrupt point for manual review.
    Does not mutate state directly.
    """
    logging.info("Executing human_review_node: Waiting for manual override or approval.")
    return {}

def invalid_input_node(state: CreditAgentState) -> dict:
    """
    Terminal node triggered when the prompt contains gibberish or non-financial text.
    """
    logging.warning("Invalid application data detected. Short-circuiting graph execution.")
    error_memo = (
        "### Invalid Application Data\n\n"
        "The submitted prompt does not contain recognizable loan terms, financial metrics, "
        "or borrower credit history. The underwriting engine cannot evaluate this profile.\n\n"
        "**Required Information:**\n"
        "* **Loan Terms:** Loan amount, term (months), interest rate, installment\n"
        "* **Financial Profile:** Annual/monthly income, DTI ratio\n"
        "* **Credit Indicators:** Past bankruptcies, derogatory public records, open accounts\n\n"
        "*Please provide structured loan details to proceed with due diligence.*"
    )
    return {"underwriting_memo": error_memo}

def route_after_extraction(state: CreditAgentState) -> str:
    """
    Routes to ML scoring only if valid credit information was extracted.
    """
    if not state.get("is_valid_financial_document", True):
        return "invalid_input_node"
    return "scoring_node"

def compile_graph():
    """Constructs and compiles the LangGraph state machine with memory persistence."""
    workflow = StateGraph(CreditAgentState)

    workflow.add_node("extractor_node", extractor_node)
    workflow.add_node("scoring_node", scoring_node)
    workflow.add_node("synthesizer_node", synthesizer_node)
    workflow.add_node("human_review_node", human_review_node)
    workflow.add_node("invalid_input_node", invalid_input_node)

    workflow.add_edge(START, "extractor_node")

    workflow.add_conditional_edges(
        "extractor_node",
        route_after_extraction,
        {
            "invalid_input_node": "invalid_input_node",
            "scoring_node": "scoring_node"
        }
    )

    workflow.add_conditional_edges(
        "scoring_node",
        route_after_scoring,
        {
            "synthesizer_node": "synthesizer_node",
            "human_review_node": "human_review_node"
        }
    )

    workflow.add_edge("invalid_input_node", END)
    workflow.add_edge("synthesizer_node", END)
    workflow.add_edge("human_review_node", "synthesizer_node")

    memory = MemorySaver()
    logging.info("StateGraph assembled and compiled successfully with MemorySaver.")

    return workflow.compile(
        checkpointer=memory,
        interrupt_before=["human_review_node"]
    )