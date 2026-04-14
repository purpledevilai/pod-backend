"""Pod bin system — standard council, no preferences set yet (auto-set E2E).

User has a freestanding Pod bin system and a standard 3-bin council.
pod_bin_preferences is NOT set. Pod should silently infer the standard 1:1 mapping,
call set_pod_bin_preferences without asking the user, then classify correctly.

This is a full E2E test — creates a real user in DynamoDB so the tool call succeeds.
"""

import json
import boto3
from uuid import uuid4
from datetime import datetime, timedelta, timezone
import jwt as pyjwt

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessFalse, AssertCalledTool,
)
from tests import r_y_lg_fogo, COUNCILS

name = "pod_bin_std_auto_set"
description = (
    "User has a freestanding Pod system and a standard 3-bin council but pod_bin_preferences "
    "is not yet set. Pod should silently call set_pod_bin_preferences with the inferred standard "
    "mapping (no questions to the user), then recommend the correct Pod bin colour for the item."
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
            "bin_system": r_y_lg_fogo,
            "pod_configuration": "freestanding",
            "pod_bin_preferences": None,
            "points": 0,
        })

        sim = SimAgent(
            session,
            persona=(
                "You have a Pod home bin system. You want to know which Pod bin to use "
                "for a plastic water bottle. Respond naturally. If Pod asks you any setup "
                "questions about your bins, answer them. Call end_test once you have received "
                "a clear bin recommendation."
            ),
            first_message="Hi, I need to throw away a plastic water bottle — which bin does it go in?",
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

        run_conversation(sim, target, max_turns=20)

        target.check_all([
            AssertCalledTool("set_pod_bin_preferences"),
            AssessTrue("Pod called set_pod_bin_preferences to save the bin preference configuration"),
            AssessTrue("Pod recommended the yellow Pod bin for the plastic water bottle"),
            AssessFalse("Pod asked the user questions about how to configure their Pod bins"),
            AssessFalse("Pod referred to a kerbside bin as the final recommendation instead of the Pod bin"),
        ])

    finally:
        table.delete_item(Key={"id": user_id})
