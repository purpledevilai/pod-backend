"""No garden in either bin: agent should acknowledge and suggest alternatives."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessScore, AssertNotCalledTool,
)
from tests import r_nogo_y, make_user_data, make_target_args

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

    user_data = make_user_data("nogo-garden", r_nogo_y)
    prompt_args, user_defined = make_target_args(user_data)

    target = TargetContext(
        session,
        agent_id=session.env("POD_AGENT_ID"),
        prompt_args=prompt_args,
        user_defined=user_defined,
    )

    run_conversation(sim, target, max_turns=15)

    target.check_all([
        AssertNotCalledTool("show_bin"),
        AssessTrue("Pod indicated that the tree branches cannot go in any of the user's kerbside bins"),
        AssessTrue(
            "Pod suggested an alternative for the tree branches such as a transfer station, "
            "green waste drop-off, or composting"
        ),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
