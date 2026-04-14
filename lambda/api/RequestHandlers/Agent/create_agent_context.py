import os
import json
import requests
from pydantic import BaseModel
from Models.HandlerPayload import HandlerPayload
from Models.User import resolve_user


class CreateAgentContextResponse(BaseModel):
    context_id: str
    client_api_key: str


def handler(payload: HandlerPayload) -> CreateAgentContextResponse:
    logger = payload.logger
    user = payload.user

    ajentify_api_url = os.getenv("AJENTIFY_API_URL", "https://api.ajentify.com")
    api_key = os.getenv("AJENTIFY_API_KEY")
    org_id = os.getenv("AJENTIFY_ORG_ID")
    agent_id = os.getenv("AGENT_ID")

    pod_api_url = os.getenv("POD_API_URL")

    if not api_key or not org_id or not agent_id:
        raise Exception("Missing Ajentify configuration (AJENTIFY_API_KEY, AJENTIFY_ORG_ID, or AGENT_ID)", 500)

    if not pod_api_url:
        raise Exception("Missing POD_API_URL configuration", 500)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"{api_key}",
    }

    auth_token = payload.lambda_event.headers.get("Authorization")

    resolved_user = resolve_user(user)

    user_data_json = json.dumps(resolved_user.model_dump())

    prompt_args = {
        "ARG_USER_DATA": user_data_json,
    }

    user_defined = {
        "user_auth_token": auth_token,
        "pod_api_url": pod_api_url,
        "user_data": user_data_json,
    }

    # 1. Create context on Ajentify
    logger.info(f"Creating Ajentify context for agent {agent_id}")
    context_response = requests.post(
        f"{ajentify_api_url}/context",
        headers=headers,
        json={
            "agent_id": agent_id,
            "prompt_args": prompt_args,
            "user_defined": user_defined,
        },
    )
    if context_response.status_code != 200:
        logger.error(f"Ajentify context creation failed: {context_response.text}")
        raise Exception(f"Failed to create Ajentify context: {context_response.text}", 502)

    context_data = context_response.json()
    context_id = context_data.get("context_id")
    if not context_id:
        raise Exception("Ajentify context response missing context_id", 502)

    logger.info(f"Ajentify context created: {context_id}")

    # 2. Generate a short-lived client API key
    logger.info("Generating client API key")
    api_key_response = requests.post(
        f"{ajentify_api_url}/generate-api-key",
        headers=headers,
        json={
            "org_id": org_id,
            "type": "client",
        },
    )
    if api_key_response.status_code != 200:
        logger.error(f"Client API key generation failed: {api_key_response.text}")
        raise Exception(f"Failed to generate client API key: {api_key_response.text}", 502)

    api_key_data = api_key_response.json()
    client_token = api_key_data.get("token")
    if not client_token:
        raise Exception("API key response missing token", 502)

    logger.info("Client API key generated successfully")

    return CreateAgentContextResponse(
        context_id=context_id,
        client_api_key=client_token,
    )
