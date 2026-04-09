"""Garden-only system: food waste goes to Red Garbage, NOT Lime Green."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessFalse, AssessScore,
)
from tests import r_y_lg_go, make_user_data


name = "go_food_to_garbage"
description = (
    "A user with a 3-bin system (Red Garbage, Yellow Recycling, Lime Green Garden Waste) "
    "asks where to put chicken bones. This is food waste. Critically, the Lime Green bin "
    "is Garden Waste only (acceptsFood=false), NOT FOGO. The Red Garbage bin accepts food "
    "(acceptsFood=true). Pod must direct the user to the Red Garbage bin."
)


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You are a person who has leftover chicken bones from dinner and "
            "wants to know which bin they go in. Respond naturally and call "
            "end_test once you get a clear answer."
        ),
        first_message="Hey, I've got some chicken bones — which bin do they go in?",
    )

    target = TargetContext(
        session,
        agent_id=session.env("POD_AGENT_ID"),
        prompt_args={"user_data": make_user_data("go-food", r_y_lg_go)},
    )

    run_conversation(sim, target, max_turns=15)

    target.assess_all([
        AssessTrue("Pod called show_bin_classification with the Red bin appearance"),
        AssessTrue("Pod classified the chicken bones into the Red Garbage bin"),
        AssessFalse("Directed the user to the Lime Green bin for the chicken bones"),
        AssessTrue("Pod provided educational content about recycling or the circular economy"),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
