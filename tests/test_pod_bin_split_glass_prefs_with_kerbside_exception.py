"""Pod bin system — split-recycling, prefs encode "skip Pod for glass" exception.

User has a Pod system and a 4-bin split-recycling council. Their
pod_bin_preferences explicitly say: yellow Pod handles all recycling,
BUT for glass they take it straight to the Purple kerbside bin
(bypassing the Pod).

When asked about a glass bottle, Pod must honour that exception and show
the kerbside Purple bin — not the yellow Pod bin. Verbal reply must match
the visual.
"""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessFalse, AssessScore, AssertCalledTool,
)
from tests import r_y_p_lg_fogo, make_user_data, make_target_args

name = "pod_bin_split_glass_prefs_with_kerbside_exception"
description = (
    "User has a Pod system and a 4-bin split-recycling council. pod_bin_preferences "
    "explicitly route glass straight to the Purple kerbside bin (bypassing the Pod) "
    "via the yellow Pod slot description. When the user asks about a glass bottle, "
    "Pod must honour the exception and show the Purple kerbside bin — not the "
    "yellow Pod bin — and the verbal reply must match the visual."
)

POD_BIN_PREFS = {
    "red":    "General garbage — goes into the Red kerbside bin",
    "yellow": "Mixed recycling (cardboard, containers) — goes into the Yellow kerbside bin. EXCEPTION: for glass, take it straight to the Purple kerbside bin (do NOT put glass in this Pod slot).",
    "green":  "Food and garden organics — goes into the Lime Green kerbside bin",
}


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You have an empty glass wine bottle and want to know which bin it goes in. "
            "You have a Pod home bin system. Respond naturally and BRIEFLY. Do NOT give "
            "any recycling advice yourself. Call end_test ONLY once Pod has told you "
            "which bin to use — not before."
        ),
        first_message="Hi, I have an empty glass wine bottle — which bin does it go in?",
    )

    user_data = make_user_data(
        "pod-split-glass-exception",
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
        AssessTrue(
            "Pod called show_bin with type kerbside and a Purple color for the "
            "glass bottle"
        ),
        AssessFalse(
            "Pod recommended the yellow Pod bin for the glass bottle (the prefs "
            "explicitly exclude glass from the yellow Pod slot)"
        ),
        AssessTrue(
            "Pod's verbal reply matched the visual — directed the user to take the "
            "glass bottle to the Purple kerbside bin"
        ),
        AssessTrue(
            "Pod gave a brief reason or fact about glass recycling (any practical or "
            "environmental reasoning counts)"
        ),
        AssessScore(
            "The sim user behaved as a real user (stated their item, asked for help) "
            "rather than acting like an assistant",
            min=0.7,
        ),
    ])
