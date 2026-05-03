"""3-bin FOGO system: food waste goes to Lime Green FOGO."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessScore, AssertCalledTool,
)
from tests import r_y_lg_fogo, make_user_data, make_target_args

name = "fogo_food"
description = (
    "A user with a standard 3-bin system (Red Garbage, Yellow Recycling, Lime Green FOGO) "
    "asks where to put leftover pasta. This is food waste. The Lime Green FOGO bin accepts "
    "food (acceptsFood=true). Pod should direct the user to the Lime Green FOGO bin."
)


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You are a person who has some leftover cooked pasta and wants to "
            "know which bin it goes in. Respond naturally. Call end_test ONLY "
            "once Pod has BOTH told you which bin AND told you how many points "
            "you earned for the classification — not before."
        ),
        first_message="Hey, I have some leftover pasta — which bin should it go in?",
    )

    user_data = make_user_data("fogo-food", r_y_lg_fogo)
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
        AssessTrue("Pod called show_bin with type kerbside and a Lime Green color"),
        AssessTrue("Pod classified the leftover pasta into the Lime Green FOGO bin"),
        AssessTrue("Pod gave the user a brief reason, fact, or explanation about why the item belongs in this bin or why it should be disposed of this way (any practical or environmental reasoning counts)"),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
