import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from src.entity.state import CreditAgentState
from src.config.configuration import ConfigurationManager
from src.logging.logger import logging

def synthesizer_node(state: CreditAgentState) -> dict:
    """
    Consolidates the raw text, extracted structured features, and the API risk scores
    to draft a formal Credit Due Diligence Memorandum using Gemini Flash Lite.
    """
    logging.info("Executing synthesizer_node: Drafting underwriting memo.")
    
    raw_text = state.get("raw_document", "")
    features = state.get("extracted_features", {})
    prediction = state.get("risk_prediction")
    probability = state.get("risk_probability")
    
    if prediction is None or not features:
        logging.error("synthesizer_node failed: Missing upstream state data (features or prediction).")
        raise ValueError("Cannot synthesize memo: Incomplete state data.")
        
    config = ConfigurationManager().get_model_config()
    
    llm = ChatGoogleGenerativeAI(
        model=config.model_name,
        max_retries=config.max_retries
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Senior Credit Risk Officer. Draft a formal, highly professional Credit Due Diligence Memorandum in Markdown format. 
        
        You must incorporate:
        1. Context from the Raw Document.
        2. Specific financial ratios and metrics from the Extracted Features.
        3. The definitive Risk Prediction (0 = Low Risk / Approve, 1 = High Risk / Escalate) and its associated Probability.
        
        Structure the memo with the following headers:
        - Executive Summary
        - Financial Profile & Ratios
        - Model Risk Assessment
        - Final Recommendation"""),
        ("user", "Raw Document:\n{raw_text}\n\nExtracted Features:\n{features}\n\nRisk Prediction: {prediction} (Probability of Default: {probability})")
    ])
    
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "raw_text": raw_text,
            "features": json.dumps(features, indent=2),
            "prediction": prediction,
            "probability": probability
        })
        
        logging.info("Underwriting memo drafted successfully.")

        return {"underwriting_memo": response.content}
        
    except Exception as e:
        logging.error(f"Failed to synthesize memo in synthesizer_node: {e}")
        raise e