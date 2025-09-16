import json
import decimal
import boto3
from typing import TypedDict, Optional, Dict, Any
from enum import Enum


# Dumb thing to handle decimal types
def default_type_error_handler(obj):
    if isinstance(obj, decimal.Decimal):
        return int(obj)
    if isinstance(obj, Enum):
        return obj.value
    raise Exception(f"Object of type {type(obj)} with value of {repr(obj)} is not JSON serializable")

class APIGatewayResponse(TypedDict):
    statusCode: int
    headers: dict
    body: str

class APIKeyInfo(TypedDict):
    id: str
    name: str
    description: Optional[str]
    enabled: bool
    created_date: str
    last_updated_date: str
    stage_keys: list
    customer_id: Optional[str]
    tags: Optional[Dict[str, str]]

def create_api_gateway_response(status_code, body, return_type) -> APIGatewayResponse:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": return_type,
            "Access-Control-Allow-Origin": "*",  # Allow requests from any origin
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",  # Allow these headers
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"  # Allow specific methods
        },
        "body": json.dumps(body, default=default_type_error_handler) if return_type == 'application/json' else body
    }

def verify_api_key(api_key: str) -> APIKeyInfo:
    # Initialize the API Gateway client
    apigateway_client = boto3.client('apigateway')
    
    # Get API key information
    response = apigateway_client.get_api_key(
        apiKey=api_key,
        includeValue=True
    )
    
    # Check if the key is enabled
    if not response.get('enabled', False):
        raise Exception("API key is not enabled")
        
    # Return the API key information
    return APIKeyInfo(
        id=response.get('id', ''),
        name=response.get('name', ''),
        description=response.get('description'),
        enabled=response.get('enabled', False),
        created_date=response.get('createdDate', '').isoformat() if response.get('createdDate') else '',
        last_updated_date=response.get('lastUpdatedDate', '').isoformat() if response.get('lastUpdatedDate') else '',
        stage_keys=response.get('stageKeys', []),
        customer_id=response.get('customerId'),
        tags=response.get('tags')
    )
