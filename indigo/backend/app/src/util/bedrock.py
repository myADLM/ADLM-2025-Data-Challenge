import json
from time import time
from app.src.util.aws import get_bedrock_client


def query_model(
    system,
    message,
    max_attempts=7,
    base_delay=0.5,
    backoff_factor=2,
    model_id="amazon.nova-pro-v1:0",
):
    """
    Query Amazon Bedrock's Nova Pro model with retry logic and error handling.

    Args:
        system (str): System prompt/context to provide to the model
        message (str): User message/query to send to the model
        max_attempts (int): Maximum number of retry attempts for throttling (default: 7)
        base_delay (float): Base delay in seconds for exponential backoff (default: 0.5)
        backoff_factor (float): Multiplier for exponential backoff (default: 2)

    Returns:
        dict: Parsed JSON response from the model

    Raises:
        Exception: If max retry attempts are exceeded or other errors occur
    """
    bedrock = get_bedrock_client()

    payload = {
        "schemaVersion": "messages-v1",
        "system": [{"text": system}],
        "messages": [{"role": "user", "content": [{"text": message}]}],
        "inferenceConfig": {"temperature": 0.7, "maxTokens": 10000},
    }

    attempt = 0
    for _ in range(max_attempts):
        try:
            response = bedrock.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(payload),
            )
            response = json.loads(response["body"].read())
            return response["output"]["message"]["content"][0]["text"].strip()
        except bedrock.exceptions.ThrottlingException:
            pass
        delay = base_delay * (backoff_factor ** (attempt - 1))
        time.sleep(delay)
    raise Exception("Giving up after %d throttling retries", attempt)
