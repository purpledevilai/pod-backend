"""3-bin FOGO system: garden organic goes to Lime Green FOGO."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessScore,
)
from tests import r_y_lg_fogo, make_user_data

name = "fogo_garden"
description = (
    "A user with a standard 3-bin system (Red Garbage, Yellow Recycling, Lime Green FOGO) "
    "asks where to put grass clippings. This is garden organic waste. The Lime Green FOGO "
    "bin accepts garden waste (acceptsGarden=true). Pod should direct the user to the "
    "Lime Green FOGO bin."
)


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You are a person who just mowed the lawn and has a pile of grass "
            "clippings. You want to know which bin they go in. Respond naturally "
            "and call end_test once you get a clear answer."
        ),
        first_message="Hi, I've got a bunch of grass clippings — where do they go?",
    )

    target = TargetContext(
        session,
        agent_id=session.env("POD_AGENT_ID"),
        prompt_args={"user_data": make_user_data("fogo-garden", r_y_lg_fogo)},
    )

    run_conversation(sim, target, max_turns=15)

    target.assess_all([
        AssessTrue("Pod called show_bin_classification with the Lime Green bin appearance"),
        AssessTrue("Pod classified the grass clippings into the Lime Green FOGO bin"),
        AssessTrue("Pod provided educational content about recycling or the circular economy"),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
