"""Split recycling (Yellow + Blue): cardboard goes to Blue Recycling."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessFalse, AssessScore,
)
from tests import r_y_b_lg_fogo, make_user_data

name = "split_recycling_cardboard"
description = (
    "A user with a 4-bin split recycling system (Red Garbage, Yellow Recycling, Blue "
    "Recycling, Lime Green Garden Waste) asks where to put a cardboard box. In this system, "
    "cardboard goes in the Blue Recycling bin (acceptsCardboard=true) while the Yellow "
    "Recycling bin does NOT accept cardboard (acceptsCardboard=false). Pod must direct the "
    "user to the Blue bin."
)


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You are a person who has a large cardboard box and wants to know "
            "which bin it goes in. Respond naturally and call end_test once "
            "you get a clear answer."
        ),
        first_message="Hey, I've got a big cardboard box — which bin does it go in?",
    )

    target = TargetContext(
        session,
        agent_id=session.env("POD_AGENT_ID"),
        prompt_args={"user_data": make_user_data("split-cardboard", r_y_b_lg_fogo)},
    )

    run_conversation(sim, target, max_turns=15)

    target.assess_all([
        AssessTrue("Pod called show_bin_classification with the Blue bin appearance"),
        AssessTrue("Pod classified the cardboard box into the Blue Recycling bin"),
        AssessFalse("Directed the user to the Yellow Recycling bin for the cardboard box"),
        AssessTrue("Pod provided educational content about recycling or the circular economy"),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
