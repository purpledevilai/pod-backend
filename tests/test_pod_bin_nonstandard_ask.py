"""Pod bin system — non-standard colour council, no preferences set (ask user E2E).

User has a Pod bin system and a council that uses a Green bin for garbage (non-standard).
pod_bin_preferences is NOT set. Pod should recognise the non-standard colour scheme,
ask the user which Pod bin they want to use for garbage (the green kerbside bin),
then call set_pod_bin_preferences with the user's chosen mapping.

This is a full E2E test — creates a real user in DynamoDB so the tool call succeeds.
"""

import json
import boto3
from uuid import uuid4
from datetime import datetime, timedelta, timezone
import jwt as pyjwt

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssertCalledTool,
)
from tests import g_y, COUNCILS

name = "pod_bin_nonstandard_ask"
description = (
    "User has a Pod system and a 2-bin green-garbage council but pod_bin_preferences is not set. "
    "Pod should detect the non-standard colour scheme, ask the user how they want to map their "
    "Pod bins, then call set_pod_bin_preferences with the gathered mapping."
)

USERS_TABLE = "users"
AWS_REGION = "ap-southeast-2"


def run(session):
    user_id = f"test-{uuid4()}"
    email = f"{user_id}@test.com"
    council = COUNCILS["7"]
    now = int(datetime.now(timezone.utc).timestamp())

    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    table = dynamodb.Table(USERS_TABLE)

    table.put_item(Item={
        "id": user_id,
        "email": email,
        "council_id": council["id"],
        "bin_system_id": g_y["id"],
        "pod_configuration": "freestanding",
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
            "bin_system": g_y,
            "pod_configuration": "freestanding",
            "pod_bin_preferences": None,
            "points": 0,
        })

        sim = SimAgent(
            session,
            persona=(
                "You have a Pod home bin system. Your council uses a green bin for garbage "
                "and a yellow bin for recycling. "
                "Do NOT volunteer your bin preferences until Pod explicitly asks you which "
                "Pod bin you want to use for each type of waste — wait for Pod to ask first. "
                "When Pod asks about your Pod bin setup, tell it: "
                "you want to use your red Pod bin for garbage and your yellow Pod bin for recycling. "
                "After Pod has set up your bins, ask it which Pod bin to use for a banana peel. "
                "Call end_test ONLY once Pod has BOTH told you which Pod bin for the banana peel "
                "AND told you told you which bin to use — not before."
            ),
            first_message="Hi, I have a Pod bin system and need some help setting it up.",
        )

        target = TargetContext(
            session,
            agent_id=session.env("POD_AGENT_ID"),
            prompt_args={"ARG_USER_DATA": user_data},
            user_defined={
                "user_auth_token": f"Bearer {access_token}",
                "pod_api_url": session.env("POD_API_URL"),
                "user_data": user_data,
            },
        )

        run_conversation(sim, target, max_turns=25)

        target.check_all([
            AssertCalledTool("set_pod_bin_preferences"),
            AssertCalledTool("show_bin", with_params={"show_reward": True, "points": 5}),
            AssessTrue(
                "Pod engaged in conversation to understand how the user wants to configure "
                "their Pod bins, either by asking directly or by indicating it would help "
                "set up the bins for the non-standard colour scheme"
            ),
            AssessTrue(
                "Pod called set_pod_bin_preferences with a mapping that assigns the red Pod bin "
                "to garbage (destined for the green kerbside bin) and the yellow Pod bin to recycling"
            ),
            AssessTrue("Pod recommended the red Pod bin for the banana peel (garbage in a green kerbside council)"),
        ])

    finally:
        table.delete_item(Key={"id": user_id})
