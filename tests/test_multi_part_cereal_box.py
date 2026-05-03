"""Multi-component item: cereal box (cardboard) + soft-plastic liner go to DIFFERENT bins.

Uses the standard 3-bin FOGO system where:
- Cardboard (the box itself) → Yellow Recycling
- Soft Plastic (the liner) → Red Garbage (Yellow doesn't accept soft plastics in this
  council, and the Red bin's acceptsSoftPlastics=true marks it as the destination for
  soft plastics in the absence of a kerbside soft-plastics stream)

Pod must:
- Recognise the item has two components and ask the user to confirm.
- Classify each component (sort_item ×2) — order doesn't matter.
- Make ONE show_bin call with bins=[{kerbside, Yellow}, {kerbside, Red}] (in either order),
  show_reward=true, points=10 (5 × 2 components).
- Speak about both bins and educate.

This is a real-DB E2E test — creates a real user with points=0 and a JWT so the
show_bin tool actually persists the points increment via /reward-points. After the
classification we assert the user's row in DynamoDB ended up at points=10.
"""

import json
import boto3
from uuid import uuid4
from datetime import datetime, timedelta, timezone
import jwt as pyjwt

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessFalse, AssessScore, AssertCalledTool,
)
from tests import r_y_lg_fogo, COUNCILS

name = "multi_part_cereal_box"
description = (
    "A user with a standard 3-bin FOGO system asks where to put a cereal box that "
    "still has its soft-plastic liner inside. The cardboard box goes to Yellow Recycling "
    "and the soft-plastic liner goes to Red Garbage. Pod must clarify that both parts "
    "are present, sort_item each one, then make ONE show_bin call with both destination "
    "bins in the bins array, show_reward=true, points=10 (5 per component). The user's "
    "row in DynamoDB should end up at points=10."
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
                "You are Sam. You have finished a cereal box and the soft-plastic "
                "liner is still inside it. Behaviour rules:\n"
                "- If Pod asks whether the liner is still in the box, confirm that it is.\n"
                "- If Pod tells you about a bin only for the cardboard box without "
                "  also handling the soft-plastic liner separately, push back: \"Wait — "
                "  what about the soft plastic liner that was still inside?\".\n"
                "- Keep the conversation going until Pod has explained where BOTH the "
                "  cardboard box AND the soft-plastic liner go.\n"
                "- Respond naturally and BRIEFLY, like a real user texting.\n"
                "- Do NOT give recycling advice yourself; you are the USER, not the assistant.\n"
                "- Call end_test ONLY once Pod has named both bins."
            ),
            first_message="Hey, I've just finished a box of cereal — which bin does it go in?",
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
            AssertCalledTool("show_bin", with_params={"show_reward": True, "points": 10}),
            AssessTrue(
                "Pod asked the user whether the soft-plastic liner was still inside "
                "the cereal box before classifying"
            ),
            AssessTrue(
                "Pod called show_bin EXACTLY ONCE, and that call's bins array contained "
                "two entries — one with color 'Yellow' (for the cardboard box) and one with "
                "color 'Red' (for the soft-plastic liner). Order between them does not matter."
            ),
            AssessTrue(
                "Pod explained why the cereal box and the soft-plastic liner needed to be "
                "separated into different bins"
            ),
            AssessFalse(
                "Pod classified the cereal box as a single item without addressing the liner"
            ),
            AssessFalse(
                "Pod used the word 'sort' or 'sorting' in any user-facing message"
            ),
            AssessScore(
                "The sim user behaved as a real user (stated their item, answered Pod's "
                "clarifying question, asked for help) rather than acting like an assistant",
                min=0.7,
            ),
        ])

        # Real DB integration assertion: 2 components × 5 points = 10
        refreshed = table.get_item(Key={"id": user_id})["Item"]
        assert int(refreshed["points"]) == 10, (
            f"Expected points to be 10 after multi-part classification (5 per component), "
            f"got {refreshed['points']}"
        )

    finally:
        table.delete_item(Key={"id": user_id})
