"""Garden-only system: food waste goes to Red Garbage, NOT Lime Green."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessFalse, AssessScore, AssertCalledTool,
)
from tests import r_y_lg_go, make_user_data, make_target_args


name = "go_food_to_garbage"
description = (
    "A user with a 3-bin system (Red Garbage, Yellow Recycling, Lime Green Garden Waste) "
    "asks where to put chicken bones. This is food waste. Critically, the Lime Green bin "
    "is Garden Waste only (acceptsFood=false), NOT FOGO. The Red Garbage bin accepts food "
    "(acceptsFood=true). Pod must direct the user to the Red Garbage bin."
)


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You are a person who has leftover chicken bones from dinner and "
            "wants to know which bin they go in. Respond naturally. Call "
            "end_test ONLY once Pod has told you which bin to use — not before."
        ),
        first_message="Hey, I've got some chicken bones — which bin do they go in?",
    )

    user_data = make_user_data("go-food", r_y_lg_go)
    prompt_args, user_defined = make_target_args(user_data)

    target = TargetContext(
        session,
        agent_id=session.env("POD_AGENT_ID"),
        prompt_args=prompt_args,
        user_defined=user_defined,
    )

    run_conversation(sim, target, max_turns=15)

    target.check_all([
        AssertCalledTool("sort_item"),
        AssertCalledTool("show_bin", with_params={"show_reward": True, "points": 5}),
        AssessTrue("Pod called show_bin with type kerbside and a Red color"),
        AssessTrue("Pod classified the chicken bones into the Red Garbage bin"),
        AssessFalse("Directed the user to the Lime Green bin for the chicken bones"),
        AssessTrue("Pod gave the user a brief reason, fact, or explanation about why the item belongs in this bin or why it should be disposed of this way (any practical or environmental reasoning counts)"),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
