"""3-bin FOGO system: chip bag (soft plastic) goes to Red Garbage."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessFalse, AssessScore, AssertCalledTool,
)
from tests import r_y_lg_fogo, make_user_data, make_target_args

name = "fogo_chip_bag"
description = (
    "A user with a standard 3-bin system (Red Garbage, Yellow Recycling, Lime Green FOGO) "
    "asks where to put an empty chip bag. A chip bag is a soft plastic. In this system, "
    "the Red Garbage bin accepts soft plastics (acceptsSoftPlastics=true) but the Yellow "
    "Recycling bin does NOT. Pod must direct the user to the Red Garbage bin."
)


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You are a person who has an empty chip bag (the crinkly foil-lined "
            "soft plastic kind) and wants to know which bin it goes in. Respond "
            "naturally. Call end_test ONLY once Pod has BOTH told you which bin "
            "AND told you told you which bin to use — not before."
        ),
        first_message="Hey, I have an empty chip packet — which bin does it go in?",
    )

    user_data = make_user_data("fogo-chipbag", r_y_lg_fogo)
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
        AssessTrue("Pod called show_bin with type kerbside and a Red color"),
        AssessTrue("Pod classified the chip bag (soft plastic) into the Red Garbage bin"),
        AssessFalse("Directed the user to the Yellow Recycling bin for the chip bag"),
        AssessTrue("Pod gave the user a brief reason, fact, or explanation about why the item belongs in this bin or why it should be disposed of this way (any practical or environmental reasoning counts)"),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
