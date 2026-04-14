"""3-bin FOGO system: general garbage goes to Red Garbage."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessScore, AssertCalledTool,
)
from tests import r_y_lg_fogo, make_user_data, make_target_args

name = "fogo_garbage"
description = (
    "A user with a standard 3-bin system (Red Garbage, Yellow Recycling, Lime Green FOGO) "
    "asks where to put a broken ceramic mug. This is general garbage — not recyclable, not "
    "organic. Pod should direct it to the Red Garbage bin."
)


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You are a person who has a broken ceramic mug and wants to know "
            "which bin it goes in. Respond naturally and call end_test once "
            "you get a clear answer."
        ),
        first_message="Hi, I have a broken ceramic mug — which bin does it go in?",
    )

    user_data = make_user_data("fogo-garbage", r_y_lg_fogo)
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
        AssessTrue("Pod called show_bin with type kerbside and a Red color"),
        AssessTrue("Pod classified the broken ceramic mug into the Red Garbage bin"),
        AssessTrue("Pod provided educational content about recycling or the circular economy"),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
