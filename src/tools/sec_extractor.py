import os
from src.logging.logger import logging

def clean_financial_text(raw_text: str) -> str:
    """Removes excess whitespace and normalizes line breaks for clean LLM ingestion."""
    return " ".join(raw_text.split())

def load_financial_document(filepath: str) -> str:
    """
    Reads and cleans an unstructured financial document (e.g., SEC 10-K text extract) from disk.
    """
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Document not found at: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            
        cleaned_content = clean_financial_text(content)
        logging.info(f"Successfully loaded and cleaned document: {filepath} ({len(cleaned_content)} characters)")
        
        return cleaned_content
        
    except Exception as e:
        logging.error(f"Failed to load document at {filepath}: {e}")
        raise e