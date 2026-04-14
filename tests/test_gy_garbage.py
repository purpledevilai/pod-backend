"""Green + Yellow system: general garbage goes to Green Garbage."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessScore, AssertCalledTool,
)
from tests import g_y, make_user_data, make_target_args

name = "gy_garbage"
description = (
    "A user with a 2-bin system (Green Garbage, Yellow Recycling) asks where to put a "
    "used disposable nappy. This is general garbage. The Green Garbage bin accepts garbage "
    "(acceptsGarbage=true). Pod should direct the user to the Green Garbage bin."
)


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You are a person who has a used disposable nappy and wants to "
            "know which bin it goes in. Respond naturally and call end_test "
            "once you get a clear answer."
        ),
        first_message="Hi, I have a used nappy — which bin does it go in?",
    )

    user_data = make_user_data("gy-garbage", g_y)
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
        AssessTrue("Pod called show_bin with type kerbside and a Green color"),
        AssessTrue("Pod classified the disposable nappy into the Green Garbage bin"),
        AssessTrue("Pod mentioned something educational about recycling, contamination, the circular economy, or the environmental impact of proper waste sorting"),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
