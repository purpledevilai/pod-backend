"""Split recycling (Yellow + Purple): glass goes to Purple Recycling."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessFalse, AssessScore, AssertCalledTool,
)
from tests import r_y_p_lg_fogo, make_user_data, make_target_args

name = "split_recycling_glass"
description = (
    "A user with a 4-bin split recycling system (Red Garbage, Yellow Recycling, Purple "
    "Recycling, Lime Green FOGO) asks where to put a glass wine bottle. In this system, "
    "glass goes in the Purple Recycling bin (acceptsGlass=true) while the Yellow Recycling "
    "bin does NOT accept glass (acceptsGlass=false). Pod must direct the user to the "
    "Purple bin."
)


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You are a person who has an empty glass wine bottle and wants to "
            "know which bin it goes in. Respond naturally and call end_test "
            "once you get a clear answer."
        ),
        first_message="Hi, I have an empty wine bottle — which bin does it go in?",
    )

    user_data = make_user_data("split-glass", r_y_p_lg_fogo)
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
        AssessTrue("Pod called show_bin with type kerbside and a Purple color"),
        AssessTrue("Pod classified the glass wine bottle into the Purple Recycling bin"),
        AssessFalse("Directed the user to the Yellow Recycling bin for the glass bottle"),
        AssessTrue("Pod provided educational content about recycling or the circular economy"),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
