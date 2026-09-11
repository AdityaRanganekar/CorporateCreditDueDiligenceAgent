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

def compile_graph():
    """Constructs and compiles the LangGraph state machine with memory persistence."""
    workflow = StateGraph(CreditAgentState)

    workflow.add_node("extractor_node", extractor_node)
    workflow.add_node("scoring_node", scoring_node)
    workflow.add_node("synthesizer_node", synthesizer_node)
    workflow.add_node("human_review_node", human_review_node)

    workflow.add_edge(START, "extractor_node")
    workflow.add_edge("extractor_node", "scoring_node")

    workflow.add_conditional_edges(
        "scoring_node",
        route_after_scoring,
        {
            "synthesizer_node": "synthesizer_node",
            "human_review_node": "human_review_node"
        }
    )

    workflow.add_edge("synthesizer_node", END)
    workflow.add_edge("human_review_node", "synthesizer_node")

    memory = MemorySaver()
    logging.info("StateGraph assembled and compiled successfully with MemorySaver.")

    return workflow.compile(
        checkpointer=memory,
        interrupt_before=["human_review_node"]
    )