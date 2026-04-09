"""No recycling bin: user has Garbage + FOGO only. Recyclable item should go to Garbage."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessScore,
)
from tests import no_recycling_system, make_user_data

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
            "wants to know which bin it goes in. Respond naturally and call "
            "end_test once you get a clear answer."
        ),
        first_message="Hi, I have an empty glass jar — which bin should it go in?",
    )

    target = TargetContext(
        session,
        agent_id=session.env("POD_AGENT_ID"),
        prompt_args={"user_data": make_user_data("norecycling", no_recycling_system)},
    )

    run_conversation(sim, target, max_turns=15)

    target.assess_all([
        AssessTrue("Pod called show_bin_classification with the Green bin appearance"),
        AssessTrue("Pod classified the glass jar into the Green Garbage bin"),
        AssessTrue("Pod provided educational content about recycling or the circular economy"),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
