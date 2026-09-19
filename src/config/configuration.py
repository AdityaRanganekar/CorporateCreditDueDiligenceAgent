import os
from dataclasses import dataclass
from src.utils.common import read_yaml
from src.logging.logger import logging

@dataclass
class ModelConfig:
    model_name: str
    max_retries: int

@dataclass
class APIConfig:
    credit_scoring_url: str
    timeout_seconds: float

class ConfigurationManager:
    def __init__(self, config_filepath: str = "config/config.yaml"):
        self.config = read_yaml(config_filepath)

    def get_model_config(self) -> ModelConfig:
        config = self.config["model_settings"]
        logging.info("Model configuration extracted successfully.")
        return ModelConfig(
            model_name=config["model_name"],
            max_retries=config["max_retries"]
        )

    def get_api_config(self) -> APIConfig:
        config = self.config["api_settings"]
        logging.info("API configuration extracted successfully.")

        scoring_url = os.getenv("CREDIT_SCORING_URL", config["credit_scoring_url"])
        
        return APIConfig(
            credit_scoring_url=scoring_url,
            timeout_seconds=config["timeout_seconds"]
        )