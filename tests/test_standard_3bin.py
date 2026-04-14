"""Standard 3-bin system: plastic bottle should go to Yellow Recycling."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessScore, AssertCalledTool,
)
from tests import r_y_lg_fogo, make_user_data, make_target_args

name = "standard_3bin"
description = (
    "A user with a standard 3-bin system (Red Garbage, Yellow Recycling, "
    "Lime Green FOGO) asks where to put a plastic water bottle. Pod should "
    "classify it as a container and direct it to the Yellow Recycling bin."
)


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You are a normal person who needs help figuring out which bin "
            "to put a plastic water bottle in. You have a standard 3-bin "
            "system. Respond naturally and call end_test once you get a "
            "clear bin classification."
        ),
        first_message="Hi, I have a plastic water bottle — which bin does it go in?",
    )

    user_data = make_user_data("standard", r_y_lg_fogo)
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
        AssertCalledTool("show_bin"),
        AssessTrue("Pod called show_bin with type kerbside and a Yellow color"),
        AssessTrue("Pod classified the plastic water bottle into the Yellow Recycling bin"),
        AssessTrue("Pod provided educational content about recycling or the circular economy"),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
