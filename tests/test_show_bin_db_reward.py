"""End-to-end: a single classification fires show_bin with show_reward=true / points=5,
which causes the show_bin tool to call /reward-points and increment the user's row in
DynamoDB from 0 to 5.

Mirrors the test_set_user_name.py pattern — creates a real user with points=0, signs a
JWT so show_bin's HTTP call to /reward-points authenticates, runs a single classification
conversation, then asserts the DynamoDB row's points field went from 0 to 5.
"""

import json
import boto3
from uuid import uuid4
from datetime import datetime, timedelta, timezone
import jwt as pyjwt

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssertCalledTool,
)
from tests import r_y_lg_fogo, COUNCILS

name = "show_bin_db_reward"
description = (
    "Real-DB integration test for show_bin's reward path and the /reward-points endpoint. "
    "Creates a user with points=0, runs a single classification (water bottle → Yellow), "
    "asserts show_bin was called with show_reward=true and points=5, then asserts the "
    "user's points field in DynamoDB was incremented from 0 to exactly 5."
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
        "name": "Sam",
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
            "name": "Sam",
            "council": council,
            "bin_system": r_y_lg_fogo,
            "pod_configuration": "none",
            "points": 0,
        })

        sim = SimAgent(
            session,
            persona=(
                "You are Sam. You have an empty plastic water bottle and want to "
                "know which bin it goes in. Respond naturally and BRIEFLY. Do NOT "
                "give recycling advice yourself; you are the USER. Call end_test "
                "ONLY once Pod has told you which bin to use — not before."
            ),
            first_message="Hi, I have an empty plastic water bottle — which bin does it go in?",
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

        run_conversation(sim, target, max_turns=15)

        target.check_all([
            AssertCalledTool("show_bin", with_params={"show_reward": True, "points": 5}),
        ])

        # Real DB integration assertion: show_bin → /reward-points → DynamoDB.
        refreshed = table.get_item(Key={"id": user_id})["Item"]
        assert int(refreshed["points"]) == 5, (
            f"Expected points to be 5 after one classification, got {refreshed['points']}"
        )

    finally:
        table.delete_item(Key={"id": user_id})
