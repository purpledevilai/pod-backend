import os
import json
import boto3
from botocore.exceptions import ClientError

def load_secrets_from_arn() -> dict:
    """
    Loads a secret from AWS Secrets Manager using the ARN defined in the SECRET_ARN environment variable.
    All key-value pairs in the secret are set as environment variables.

    Returns:
        dict: Parsed secret values.
    """
    secret_arn = os.environ.get("SECRET_ARN")
    if not secret_arn:
        raise EnvironmentError("SECRET_ARN environment variable is not set.")

    client = boto3.client("secretsmanager")

    try:
        response = client.get_secret_value(SecretId=secret_arn)
    except ClientError as e:
        raise RuntimeError(f"Failed to retrieve secret: {e}")

    if "SecretString" in response:
        secret_dict = json.loads(response["SecretString"])
    else:
        raise ValueError("SecretString is empty or missing in the secret response.")

    # Set each key-value in the secret as an env variable
    for key, value in secret_dict.items():
        os.environ[key] = value

    return secret_dict
