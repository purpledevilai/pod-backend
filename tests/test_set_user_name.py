"""End-to-end: Pod doesn't know the user's name, asks for it, user tells it, set_user_name tool is called."""

import json
import boto3
from uuid import uuid4
from datetime import datetime, timedelta, timezone
import jwt as pyjwt

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssertCalledTool,
)
from tests import r_y_lg_fogo, COUNCILS

name = "set_user_name"
description = (
    "Pod doesn't know the user's name (name is null in user_data). "
    "Pod should ask for the user's name during the greeting. "
    "When the user provides their name, Pod should call the set_user_name "
    "tool to persist it. This test creates a real test user and auth token "
    "so the tool can make an authenticated call to the backend."
)

USERS_TABLE = "users"
AWS_REGION = "ap-southeast-2"


def run(session):
    user_id = f"test-{uuid4()}"
    email = f"{user_id}@test.com"
    council = COUNCILS["19"]
    now = int(datetime.now(timezone.utc).timestamp())

    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    table = dynamodb.Table(USERS_TABLE)

    table.put_item(Item={
        "id": user_id,
        "email": email,
        "council_id": council["id"],
        "bin_system_id": r_y_lg_fogo["id"],
        "pod_configuration": "none",
        "points": 0,
        "created_at": now,
        "updated_at": now,
    })

    try:
        jwt_secret = session.env("JWT_SECRET")
        token_payload = {
            "user_id": user_id,
            "email": email,
            "token_type": "access_token",
            "iat": now,
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=15)).timestamp()),
        }
        access_token = pyjwt.encode(token_payload, jwt_secret, algorithm="HS256")

        user_data = json.dumps({
            "id": user_id,
            "email": email,
            "name": None,
            "council": council,
            "bin_system": r_y_lg_fogo,
            "pod_configuration": "none",
            "points": 0,
        })

        sim = SimAgent(
            session,
            persona=(
                "You are Alex. You want help figuring out which bin to use for a pizza box. "
                "When Pod greets you and asks your name, tell it your name is Alex. "
                "After that, ask about the pizza box. "
                "Call end_test once you have received a bin classification."
            ),
            first_message="Hey!",
        )

        target = TargetContext(
            session,
            agent_id=session.env("POD_AGENT_ID"),
            prompt_args={"user_data": user_data},
            user_defined={
                "user_auth_token": f"Bearer {access_token}",
                "pod_api_url": session.env("POD_API_URL"),
            },
        )

        run_conversation(sim, target, max_turns=20)

        target.check_all([
            AssertCalledTool("set_user_name"),
            AssessTrue("Pod asked the user for their name during the conversation"),
            AssessTrue("Pod called the set_user_name tool after the user provided their name Alex"),
        ])

    finally:
        table.delete_item(Key={"id": user_id})
