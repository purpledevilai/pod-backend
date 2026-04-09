"""3-bin FOGO system: food waste goes to Lime Green FOGO."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessScore,
)
from tests import r_y_lg_fogo, make_user_data

name = "fogo_food"
description = (
    "A user with a standard 3-bin system (Red Garbage, Yellow Recycling, Lime Green FOGO) "
    "asks where to put leftover pasta. This is food waste. The Lime Green FOGO bin accepts "
    "food (acceptsFood=true). Pod should direct the user to the Lime Green FOGO bin."
)


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You are a person who has some leftover cooked pasta and wants to "
            "know which bin it goes in. Respond naturally and call end_test "
            "once you get a clear answer."
        ),
        first_message="Hey, I have some leftover pasta — which bin should it go in?",
    )

    target = TargetContext(
        session,
        agent_id=session.env("POD_AGENT_ID"),
        prompt_args={"user_data": make_user_data("fogo-food", r_y_lg_fogo)},
    )

    run_conversation(sim, target, max_turns=15)

    target.assess_all([
        AssessTrue("Pod called show_bin_classification with the Lime Green bin appearance"),
        AssessTrue("Pod classified the leftover pasta into the Lime Green FOGO bin"),
        AssessTrue("Pod provided educational content about recycling or the circular economy"),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
