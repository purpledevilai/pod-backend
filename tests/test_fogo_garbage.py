"""3-bin FOGO system: general garbage goes to Red Garbage."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessScore,
)
from tests import r_y_lg_fogo, make_user_data

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

    target = TargetContext(
        session,
        agent_id=session.env("POD_AGENT_ID"),
        prompt_args={"user_data": make_user_data("fogo-garbage", r_y_lg_fogo)},
    )

    run_conversation(sim, target, max_turns=15)

    target.assess_all([
        AssessTrue("Pod called show_bin_classification with the Red bin appearance"),
        AssessTrue("Pod classified the broken ceramic mug into the Red Garbage bin"),
        AssessTrue("Pod provided educational content about recycling or the circular economy"),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
