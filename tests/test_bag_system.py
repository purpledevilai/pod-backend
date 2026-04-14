"""Bag-based system: aluminium can should go to Clear/Red Recycling bag."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessScore, AssertCalledTool,
)
from tests import bag_system, make_user_data, make_target_args

name = "bag_system"
description = (
    "A user with a bag-based bin system (BYO Garbage, Clear/Red Recycling, "
    "Clear/Green Food Waste) asks where to put an aluminium can. Pod must "
    "correctly reference the non-standard bag appearance 'Clear/Red' rather "
    "than a typical bin colour like 'Yellow'."
)


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You are a person at a ski resort who has an empty aluminium can "
            "(like a soft drink can) and you want to know which bag to put it in. "
            "You have an unusual bag-based waste system. Respond naturally and "
            "call end_test once you get a clear answer."
        ),
        first_message="Hey, I have an empty aluminium can — where does it go?",
    )

    user_data = make_user_data("bag-system", bag_system)
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
        AssessTrue("Pod called show_bin with type kerbside and a Clear/Red color"),
        AssessTrue(
            "Directed the user to the Clear/Red Recycling bag for the aluminium can, "
            "correctly referencing the non-standard bag appearance"
        ),
        AssessTrue("Pod provided educational content about recycling or the circular economy"),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
