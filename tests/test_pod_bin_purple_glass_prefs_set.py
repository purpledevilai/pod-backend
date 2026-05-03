"""Pod bin system — split recycling (Purple glass), preferences already configured.

User has a Pod bin system and a 4-bin council with a Purple glass recycling bin.
They've configured their green Pod bin to hold glass destined for the purple kerbside bin.
Pod should recommend the green Pod bin for a glass wine bottle — not the purple kerbside bin.
"""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessFalse, AssessScore, AssertCalledTool,
)
from tests import r_y_p_lg_fogo, make_user_data, make_target_args

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
            "for an empty glass wine bottle. Respond naturally. Call end_test ONLY "
            "once Pod has BOTH told you which Pod bin AND told you how many points "
            "you earned for the classification — not before."
        ),
        first_message="Hi, I have an empty glass wine bottle — which Pod bin does it go in?",
    )

    user_data = make_user_data(
        "pod-purple-glass",
        r_y_p_lg_fogo,
        pod_configuration="freestanding",
        pod_bin_preferences=POD_BIN_PREFS,
    )
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
        AssessTrue("Pod called show_bin with type pod and a green color"),
        AssessTrue("Pod recommended the green Pod bin for the glass wine bottle"),
        AssessFalse("Pod recommended the Purple bin or a purple kerbside bin as the final destination Pod bin"),
        AssessFalse("Pod recommended the Yellow Pod bin for the glass bottle"),
        AssessTrue("Pod gave the user a brief reason, fact, or explanation about why the item belongs in this bin or why it should be disposed of this way (any practical or environmental reasoning counts)"),
        AssessScore(
            "The sim user behaved as a real user (stated their item, asked for help) "
            "rather than acting like an assistant",
            min=0.7,
        ),
    ])
