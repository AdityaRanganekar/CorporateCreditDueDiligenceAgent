import time
import httpx
from src.logging.logger import logging
from src.config.configuration import ConfigurationManager

def score_credit_risk(payload: dict, max_retries: int = 3) -> dict:
    """
    Sends extracted features to the Credit Risk API.
    Implements latency tracking, status code validation, and exponential backoff retries.
    """
    api_config = ConfigurationManager().get_api_config()
    url = api_config.credit_scoring_url
    timeout = api_config.timeout_seconds

    for attempt in range(1, max_retries + 1):
        try:
            logging.info(f"Attempt {attempt}: Sending payload to Credit Risk API at {url}")
            start_time = time.time()

            response = httpx.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            
            latency = time.time() - start_time
            logging.info(f"API call successful. Latency: {latency:.2f} seconds.")
            
            return response.json()

        except httpx.TimeoutException:
            logging.warning(f"Timeout on attempt {attempt} after {timeout} seconds.")
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP {e.response.status_code} error on attempt {attempt}: {e.response.text}")
        except httpx.RequestError as e:
            logging.warning(f"Network error on attempt {attempt}: {e}")
            
        if attempt == max_retries:
            logging.error("Max retries reached. Credit Risk API is unreachable.")
            raise ConnectionError("Failed to fetch risk score from the deterministic API.")

        time.sleep(2 ** attempt)