"""Pod bin system — green garbage council, preferences already configured.

User has a Pod bin system and a council that uses a Green bin for garbage (non-standard).
They've configured their red Pod bin to hold garbage destined for the green kerbside bin.
Pod should recommend the red Pod bin for a broken toy (garbage).
"""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessFalse, AssessScore,
)
from tests import g_y, make_user_data

name = "pod_bin_green_garbage_prefs_set"
description = (
    "User has a Pod system and a 2-bin council that uses Green for garbage and Yellow for recycling. "
    "pod_bin_preferences maps the red Pod bin to garbage destined for the green kerbside bin. "
    "Pod should recommend the red Pod bin for a broken plastic toy (garbage), "
    "NOT the green Pod bin or green kerbside bin."
)

POD_BIN_PREFS = {
    "red":    "General garbage — goes into the Green kerbside bin",
    "yellow": "Recycling (cardboard, containers, glass) — goes into the Yellow kerbside bin",
}


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You have a Pod home bin system. You want to know which Pod bin to use "
            "for a broken plastic toy that can't be recycled. Respond naturally and "
            "call end_test once you receive a clear bin recommendation."
        ),
        first_message="Hi, I have a broken plastic toy — which Pod bin does it go in?",
    )

    target = TargetContext(
        session,
        agent_id=session.env("POD_AGENT_ID"),
        prompt_args={
            "user_data": make_user_data(
                "pod-green-garbage",
                g_y,
                pod_configuration="freestanding",
                pod_bin_preferences=POD_BIN_PREFS,
            )
        },
    )

    run_conversation(sim, target, max_turns=15)

    target.assess_all([
        AssessTrue("Pod called show_bin_classification with the Red bin appearance"),
        AssessTrue("Pod recommended the red Pod bin for the broken plastic toy"),
        AssessFalse("Pod recommended putting the toy in the green Pod bin as the primary Pod recommendation"),
        AssessTrue("Pod provided educational content about why the item goes to garbage"),
        AssessScore(
            "The sim user behaved as a real user (stated their item, asked for help) "
            "rather than acting like an assistant",
            min=0.7,
        ),
    ])
