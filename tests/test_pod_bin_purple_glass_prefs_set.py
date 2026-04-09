"""Pod bin system — split recycling (Purple glass), preferences already configured.

User has a Pod bin system and a 4-bin council with a Purple glass recycling bin.
They've configured their green Pod bin to hold glass destined for the purple kerbside bin.
Pod should recommend the green Pod bin for a glass wine bottle — not the purple kerbside bin.
"""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessFalse, AssessScore,
)
from tests import r_y_p_lg_fogo, make_user_data

name = "pod_bin_purple_glass_prefs_set"
description = (
    "User has a Pod system and a 4-bin split-recycling council (Red/Yellow/Purple glass/Lime Green FOGO). "
    "pod_bin_preferences maps the green Pod bin to glass destined for the purple kerbside bin. "
    "Pod should recommend the green Pod bin for a glass wine bottle, NOT the purple kerbside bin."
)

POD_BIN_PREFS = {
    "red":    "General garbage — goes into the Red kerbside bin",
    "yellow": "Mixed recycling (cardboard, containers) — goes into the Yellow kerbside bin",
    "green":  "Glass only — goes into the Purple kerbside glass recycling bin",
}


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You have a Pod home bin system. You want to know which Pod bin to use "
            "for an empty glass wine bottle. Respond naturally and call end_test once "
            "you receive a clear bin recommendation."
        ),
        first_message="Hi, I have an empty glass wine bottle — which Pod bin does it go in?",
    )

    target = TargetContext(
        session,
        agent_id=session.env("POD_AGENT_ID"),
        prompt_args={
            "user_data": make_user_data(
                "pod-purple-glass",
                r_y_p_lg_fogo,
                pod_configuration="freestanding",
                pod_bin_preferences=POD_BIN_PREFS,
            )
        },
    )

    run_conversation(sim, target, max_turns=15)

    target.assess_all([
        AssessTrue("Pod called show_bin_classification with the Green bin appearance"),
        AssessTrue("Pod recommended the green Pod bin for the glass wine bottle"),
        AssessFalse("Pod recommended the Purple bin or a purple kerbside bin as the final destination Pod bin"),
        AssessFalse("Pod recommended the Yellow Pod bin for the glass bottle"),
        AssessTrue("Pod provided educational content about recycling or the circular economy"),
        AssessScore(
            "The sim user behaved as a real user (stated their item, asked for help) "
            "rather than acting like an assistant",
            min=0.7,
        ),
    ])
