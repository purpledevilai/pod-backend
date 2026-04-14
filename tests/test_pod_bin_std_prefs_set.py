"""Pod bin system — standard colour council, preferences already configured.

User has a freestanding Pod bin system and a standard 3-bin council (Red/Yellow/Lime Green).
pod_bin_preferences is already set with a 1:1 mapping.
Pod should recommend the yellow Pod bin for a plastic bottle — not kerbside language.
"""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessFalse, AssessScore, AssertCalledTool,
)
from tests import r_y_lg_fogo, make_user_data, make_target_args

name = "pod_bin_std_prefs_set"
description = (
    "User has a freestanding Pod bin system and a standard 3-bin council. "
    "pod_bin_preferences is already set (red=garbage, yellow=recycling, green=FOGO). "
    "Pod should recommend the yellow Pod bin for a plastic water bottle, "
    "not use kerbside bin language."
)

POD_BIN_PREFS = {
    "red":    "General garbage — goes into the Red kerbside bin",
    "yellow": "Recycling (cardboard, containers, glass) — goes into the Yellow kerbside bin",
    "green":  "Food and garden organics — goes into the Lime Green kerbside bin",
}


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You have a Pod home bin system and want to know which Pod bin to use "
            "for a plastic water bottle. Respond naturally and call end_test once "
            "you receive a clear bin recommendation."
        ),
        first_message="Hi, I have a plastic water bottle — which Pod bin does it go in?",
    )

    user_data = make_user_data(
        "pod-std-prefs",
        r_y_lg_fogo,
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
        AssertCalledTool("show_bin"),
        AssessTrue("Pod called show_bin with type pod and a yellow color"),
        AssessTrue("Pod recommended the yellow Pod bin for the plastic water bottle"),
        AssessFalse("Pod's primary bin recommendation was a kerbside bin rather than a Pod bin (Pod may mention the kerbside destination as context, but the primary recommendation must be the Pod bin)"),
        AssessTrue("Pod provided educational content about recycling or the circular economy"),
        AssessScore(
            "The sim user behaved as a real user (stated their item, asked for help) "
            "rather than acting like an assistant",
            min=0.7,
        ),
    ])
