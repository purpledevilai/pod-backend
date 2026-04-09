"""No garden in either bin: agent should acknowledge and suggest alternatives."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessFalse, AssessScore,
)
from tests import r_nogo_y, make_user_data

name = "nogo_garden"
description = (
    "A user with a 2-bin system (Red Garbage, Yellow Recycling) where neither bin accepts "
    "garden waste (both acceptsGarden=false) asks where to put tree branches. Pod should "
    "recognise that garden waste cannot go in either bin and suggest an alternative such "
    "as a council green waste drop-off, transfer station, or composting at home."
)


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You are a person who has some small tree branches from pruning "
            "and wants to know which bin they go in. Respond naturally and "
            "call end_test once you get a clear answer or recommendation."
        ),
        first_message="Hi, I've got some tree branches — which bin should they go in?",
    )

    target = TargetContext(
        session,
        agent_id=session.env("POD_AGENT_ID"),
        prompt_args={"user_data": make_user_data("nogo-garden", r_nogo_y)},
    )

    run_conversation(sim, target, max_turns=15)

    target.assess_all([
        AssessFalse("Pod called the show_bin_classification tool for the tree branches"),
        AssessTrue("Pod acknowledged that no bin accepts garden waste in this system"),
        AssessTrue(
            "Pod suggested an alternative for the tree branches such as a transfer station, "
            "green waste drop-off, or composting"
        ),
        AssessTrue("Pod provided educational content about recycling or the circular economy"),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
