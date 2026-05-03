"""Pod bin system — split-recycling, no prefs, user picks "skip Pod for glass".

E2E test: user has a Pod system and a 4-bin split-recycling council. They
ask about a glass bottle. Pod shows the kerbside Purple bin and offers
setup options. The user picks: "I'll just walk glass straight to the
purple kerbside bin — don't bother routing it through my Pod."

Pod must then call set_pod_bin_preferences with a yellow Pod slot
description that captures the exception (glass bypasses the Pod and goes
directly to the Purple kerbside bin).

Requires a real DynamoDB user because set_pod_bin_preferences hits the
backend.
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
from tests import r_y_p_lg_fogo, COUNCILS

name = "pod_bin_split_glass_no_prefs_setup_skip_pod"
description = (
    "User has a Pod system and a 4-bin split-recycling council; pod_bin_preferences "
    "is NOT set. They ask about a glass bottle, then choose to take glass straight "
    "to the Purple kerbside bin (bypassing the Pod). Pod must show the Purple "
    "kerbside bin first, then save prefs that encode the bypass exception in the "
    "yellow Pod slot description."
)

USERS_TABLE = "users"
AWS_REGION = "ap-southeast-2"


def run(session):
    user_id = f"test-{uuid4()}"
    email = f"{user_id}@test.com"
    council = COUNCILS["60"]
    now = int(datetime.now(timezone.utc).timestamp())

    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    table = dynamodb.Table(USERS_TABLE)

    table.put_item(Item={
        "id": user_id,
        "email": email,
        "council_id": council["id"],
        "bin_system_id": r_y_p_lg_fogo["id"],
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
            "bin_system": r_y_p_lg_fogo,
            "pod_configuration": "freestanding",
            "pod_bin_preferences": None,
            "points": 0,
        })

        sim = SimAgent(
            session,
            persona=(
                "You have an empty glass wine bottle and want to know which bin it "
                "goes in. You have a Pod home bin system but have not yet decided how "
                "to use each Pod bin colour — do NOT volunteer preferences upfront. "
                "After Pod tells you which bin to use AND offers options for handling "
                "glass via your Pod going forward, REPLY: \"I'll just walk it straight "
                "out to the purple kerbside bin when I have one — don't bother routing "
                "it through my Pod.\" Then, if Pod confirms a setup, briefly "
                "acknowledge. Call end_test ONLY once Pod has confirmed your chosen "
                "arrangement back to you."
            ),
            first_message="Hi, I have an empty wine bottle — which bin does it go in?",
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
            AssertCalledTool("show_bin", with_params={"show_reward": True, "points": 5}),
            AssertCalledTool("set_pod_bin_preferences"),
            AssessTrue(
                "Pod's first show_bin call for the glass bottle used type kerbside "
                "and a Purple color (NOT type pod)"
            ),
            AssessTrue(
                "Pod called set_pod_bin_preferences with a yellow Pod slot description "
                "that explicitly tells the user to take glass straight to the Purple "
                "kerbside bin rather than routing it through the Pod"
            ),
            AssessTrue(
                "Pod confirmed the chosen arrangement (glass goes directly to Purple "
                "kerbside, bypassing the Pod) back to the user in plain language"
            ),
        ])

    finally:
        table.delete_item(Key={"id": user_id})
