"""
Lightweight AWS helpers.

This module centralizes creation and caching of AWS SDK objects used by the
application. It supports running against LocalStack when the environment
variable ``USE_LOCALSTACK=1`` is set, and otherwise defaults to real AWS.

Caching via ``functools.cache`` ensures that callers receive a single shared
instance per process for each helper, avoiding repeated client/resource
construction and making connection reuse more effective.
"""

import logging
import os
import socket
from functools import cache

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

logger = logging.getLogger("app")


@cache
def get_s3():
    """Return a cached ``boto3`` S3 resource.

    - Honors ``AWS_REGION`` (falls back to ``us-east-1``).
    - When ``USE_LOCALSTACK=1`` is present, connects to LocalStack at
      ``http://localhost:4566`` with test credentials.
    - Applies a conservative retry configuration suitable for transient
      network/Throttling errors.
    """
    region = os.getenv("AWS_REGION", "us-east-1")
    cfg = Config(retries={"max_attempts": 10, "mode": "standard"})
    if os.getenv("USE_LOCALSTACK") == "1":
        logger.info("Using LocalStack")
        # Detect if we're running in Docker by checking if 'localstack' hostname is resolvable
        try:
            socket.gethostbyname("localstack")
            # We're in Docker, use service name
            default_endpoint = "http://localstack:4566"
            logger.info("Docker environment detected, using localstack:4566")
        except socket.gaierror:
            # We're in local development, use localhost
            default_endpoint = "http://localhost:4566"
            logger.info("Local environment detected, using localhost:4566")

        endpoint_url = os.getenv("LOCALSTACK_ENDPOINT", default_endpoint)
        return boto3.resource(
            "s3",
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
            config=cfg,
        )
    logger.info(f"Using live S3")
    return boto3.resource("s3", region_name=region, config=cfg)


@cache
def get_s3_client():
    """Return a cached low-level S3 client backed by the S3 resource."""
    return get_s3().meta.client


@cache
def get_bedrock_client():
    """Return a cached Bedrock client that always uses real AWS.

    - Always connects to real AWS Bedrock service (never LocalStack)
    - Uses credentials from environment variables, AWS credentials file, or IAM roles
    - Honors AWS_REGION (falls back to us-east-1)
    - Applies retry configuration for transient errors
    """
    region = os.getenv("AWS_REGION", "us-east-1")
    cfg = Config(retries={"max_attempts": 10, "mode": "standard"})

    # Always use real AWS for Bedrock - never LocalStack
    profile_name = os.getenv("AMAZON_NOVA_PROFILE", "default")
    session = boto3.Session(profile_name=profile_name)
    
    # Log profile information for debugging
    logger.info(f"Creating Bedrock client with profile: {profile_name}")
    logger.info(f"Using AWS region: {region}")
    
    return session.client("bedrock-runtime", region_name=region, config=cfg)


def ensure_bucket(bucket_name: str):
    """Ensure an S3 bucket exists; create it if it does not.

    Performs a ``HeadBucket`` call and creates the bucket on a 404. Any other
    error is re-raised to the caller.
    """
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            client.create_bucket(Bucket=bucket_name)
            return
        raise e
