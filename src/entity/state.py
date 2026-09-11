from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class CreditAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    raw_document: str
    is_valid_financial_document: Optional[bool]
    extracted_features: Optional[dict]
    risk_prediction: Optional[int]
    risk_probability: Optional[float]
    underwriting_memo: Optional[str]