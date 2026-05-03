"""FOGO system: pizza box — Pod should clarify cleanliness before classifying."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessFalse, AssessScore, AssertCalledTool,
)
from tests import r_y_lg_fogo, make_user_data, make_target_args

name = "fogo_pizza_box"
description = (
    "A user with a standard 3-bin system asks where to put a pizza box. "
    "A pizza box is cardboard, but its correct bin depends on whether it "
    "is clean or greasy. Pod should ask the user whether the box is clean "
    "or soiled. The test user says it is clean, and Pod should then direct "
    "it to the Yellow Recycling bin."
)


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You are a person who wants to throw away a pizza box. You're not "
            "sure which bin it goes in. If the assistant asks whether the box "
            "is clean or greasy, say that it is clean with no grease stains. "
            "Respond naturally. Call end_test ONLY once Pod has BOTH told you "
            "which bin AND told you how many points you earned for the "
            "classification — not before."
        ),
        first_message="Hi, I have a pizza box — where does it go?",
    )

    user_data = make_user_data("fogo-pizzabox", r_y_lg_fogo)
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
        AssessTrue(
            "Pod asked the user whether the pizza box is clean or greasy "
            "before giving a final classification"
        ),
        AssessTrue("Pod classified the clean pizza box into the Yellow Recycling bin"),
        AssessFalse("Directed the user to the Garbage or FOGO bin for the clean pizza box"),
        AssessTrue("Pod gave the user a brief reason, fact, or explanation about why the item belongs in this bin or why it should be disposed of this way (any practical or environmental reasoning counts)"),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
