from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from src.entity.state import CreditAgentState
from src.entity.schema import CreditFeaturesSchema
from src.config.configuration import ConfigurationManager
from src.logging.logger import logging

def extractor_node(state: CreditAgentState) -> dict:
    """
    Reads the raw SEC document from the LangGraph state and uses Gemini Flash Lite
    to deterministically extract the financial features into a strict JSON payload.
    """
    logging.info("Executing extractor_node: Parsing raw document for credit features.")
    
    raw_text = state.get("raw_document", "")
    if not raw_text:
        logging.error("extractor_node failed: No raw_document found in state.")
        raise ValueError("State is missing 'raw_document'. Cannot extract features.")

    config = ConfigurationManager().get_model_config()
    
    llm = ChatGoogleGenerativeAI(
        model=config.model_name,
        max_retries=config.max_retries
    )
    
    structured_llm = llm.with_structured_output(CreditFeaturesSchema)
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert financial analyst. Analyze the provided text and extract credit risk features.\n"
            "1. If the input text is gibberish, conversational banter, or contains no identifiable loan or financial metrics, "
            "set 'is_valid_financial_document' to False.\n"
            "2. If the text contains recognizable loan or borrower information, set 'is_valid_financial_document' to True.\n"
            "3. Return numeric values strictly as numbers. If qualitative evidence of bankruptcies, defaults, or derogatory "
            "records is present without an explicit count, assign a minimum value of 1 to those fields."
        ),
        ("user", "{document}")
    ])
    
    extraction_chain = prompt | structured_llm
    
    try:
        extracted_record = extraction_chain.invoke({"document": raw_text})
        payload = extracted_record.model_dump()
        is_valid = payload.get("is_valid_financial_document", True)
        
        logging.info(f"Extractor node completed successfully. is_valid_financial_document={is_valid}")

        return {
            "extracted_features": payload,
            "is_valid_financial_document": is_valid
        }
        
    except Exception as e:
        logging.error(f"Failed to extract features in extractor_node: {e}")
        raise e