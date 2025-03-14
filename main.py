import os
import logging
from core import OpenAiClient, PDFWorker

if not os.path.exists('log'):
    os.makedirs('log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='log/run.log'
    )
logger = logging.getLogger(__name__)

def completion(message, model, system_prompt="", image_paths=None, temperature=0.5, max_tokens=8192, retry_times=3):
    """
    Call OpenAI's completion interface for text generation

    Args:
        message (str): User input message
        model (str): Model name
        system_prompt (str, optional): System prompt, defaults to empty string
        image_paths (List[str], optional): List of image paths, defaults to None
        temperature (float, optional): Temperature for text generation, defaults to 0.5
        max_tokens (int, optional): Maximum number of tokens for generated text, defaults to 8192
    Returns:
        str: Generated text content
    """
    
    # Get API key and API base URL from environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_API_BASE")

    # Initialize OpenAiClient
    client = OpenAiClient.OpenAiClient(base_url=base_url, api_key=api_key, model=model)
    # Call completion method with retry mechanism
    for _ in range(retry_times):
        try:
            response = client.completion(user_message=message, system_prompt=system_prompt, image_paths=image_paths, temperature=temperature, max_tokens=max_tokens)
            return response
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            # If retry fails, wait for a while before retrying
            time.sleep(0.5)
    return ""


if __name__ == "__main__":
    logger.info("Hello, World!")