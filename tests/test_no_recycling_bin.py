"""No recycling bin: user has Garbage + FOGO only. Recyclable item should go to Garbage."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessScore, AssertCalledTool,
)
from tests import no_recycling_system, make_user_data, make_target_args

name = "no_recycling_bin"
description = (
    "A user with only a Green Garbage bin and a Maroon FOGO bin (no Recycling bin) asks "
    "where to put a glass jar. Glass is normally recyclable, but this user's Garbage bin "
    "accepts glass (acceptsGlass=true) while FOGO does not. Pod must direct the user to "
    "the Green Garbage bin and ideally note that their council doesn't provide a separate "
    "recycling bin."
)


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You are a person who has an empty glass jar (like a jam jar) and "
            "wants to know which bin it goes in. Respond naturally. Call "
            "end_test ONLY once Pod has told you which bin to use — not before."
        ),
        first_message="Hi, I have an empty glass jar — which bin should it go in?",
    )

    user_data = make_user_data("norecycling", no_recycling_system)
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
        AssessTrue("Pod called show_bin with type kerbside and a Green color"),
        AssessTrue("Pod directed the user to put the glass jar in their green kerbside bin"),
        AssessTrue("Pod gave the user a brief reason, fact, or explanation about why the item belongs in this bin or why it should be disposed of this way (any practical or environmental reasoning counts)"),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
