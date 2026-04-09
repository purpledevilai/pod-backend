"""Soft plastics edge: bread bag (soft plastic) goes to Red Garbage, NOT Yellow Recycling."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessFalse, AssessScore,
)
from tests import r_y_lg_fogo, make_user_data

name = "soft_plastics_edge"
description = (
    "A user with a standard 3-bin system (Red Garbage, Yellow Recycling, Lime Green FOGO) "
    "asks where to put a bread bag. The bread bag is a soft plastic. In this bin system, "
    "the Red Garbage bin accepts soft plastics (acceptsSoftPlastics=true) but the Yellow "
    "Recycling bin does NOT (acceptsSoftPlastics=false). Pod must direct the user to the "
    "Red Garbage bin."
)


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You are a person who has an empty bread bag (the soft plastic kind "
            "that bread comes in) and wants to know which bin it goes in. "
            "Respond naturally and call end_test once you get a clear answer."
        ),
        first_message="Hey, I have an empty bread bag — which bin does it go in?",
    )

    target = TargetContext(
        session,
        agent_id=session.env("POD_AGENT_ID"),
        prompt_args={"user_data": make_user_data("softplastics", r_y_lg_fogo)},
    )

    run_conversation(sim, target, max_turns=15)

    target.assess_all([
        AssessTrue("Pod called show_bin_classification with the Red bin appearance"),
        AssessTrue("Pod classified the bread bag into the Red Garbage bin"),
        AssessFalse("Directed the user to the Yellow Recycling bin for the bread bag"),
        AssessTrue("Pod provided educational content about recycling or the circular economy"),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
