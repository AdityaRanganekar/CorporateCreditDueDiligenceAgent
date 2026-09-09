import os
import yaml
from src.logging.logger import logging

def read_yaml(path_to_yaml: str) -> dict:
    """Reads a yaml file and returns a dictionary."""
    try:
        with open(path_to_yaml, "r") as yaml_file:
            content = yaml.safe_load(yaml_file)
            logging.info(f"YAML file: {path_to_yaml} loaded successfully")
            return content
    except Exception as e:
        logging.error(f"Error reading YAML file at {path_to_yaml}: {e}")
        raise e

def create_directories(path_to_directories: list, verbose: bool = True):
    """Creates a list of directories."""
    for path in path_to_directories:
        os.makedirs(path, exist_ok=True)
        if verbose:
            logging.info(f"Created directory at: {path}")