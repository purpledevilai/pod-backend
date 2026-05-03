"""Soft plastics orange bag system: soft plastic goes to Yellow Recycling in an orange bag."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessScore, AssertCalledTool,
)
from tests import r_y_sp, make_user_data, make_target_args

name = "soft_plastics_orange_bag"
description = (
    "A user with a 2-bin system (Red Garbage, Yellow Recycling) where the Yellow bin "
    "accepts soft plastics via a special orange bag program (extras=['soft-plastics-orange-bag']) "
    "asks where to put a plastic shopping bag. Pod should classify it as Yellow Recycling "
    "and specifically mention that the soft plastic needs to go inside an orange bag before "
    "being placed in the Yellow bin."
)


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You are a person who has a plastic shopping bag and wants to know "
            "which bin it goes in. Respond naturally. Call end_test ONLY once "
            "Pod has told you which bin to use — not before."
        ),
        first_message="Hi, I have a plastic shopping bag — which bin does it go in?",
    )

    user_data = make_user_data("sp-orange", r_y_sp)
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
        AssessTrue("Pod called show_bin with type kerbside and a Yellow color"),
        AssessTrue("Pod classified the plastic shopping bag into the Yellow Recycling bin"),
        AssessTrue("Pod mentioned or referenced the orange bag program for soft plastics"),
        AssessTrue("Pod gave the user a brief reason, fact, or explanation about why the item belongs in this bin or why it should be disposed of this way (any practical or environmental reasoning counts)"),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
