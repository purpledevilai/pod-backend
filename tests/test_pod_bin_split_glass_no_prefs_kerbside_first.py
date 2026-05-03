"""Pod bin system — split-recycling council, no prefs, kerbside-first behaviour.

User has a Pod system and a 4-bin split-recycling council (Yarra-shape:
Red Garbage, Yellow Recycling, Purple Recycling for glass, Lime Green FOGO).
pod_bin_preferences is NOT set.

Because there is no clean 1:1 mapping for glass (Purple kerbside has no
matching Pod colour), Pod must default to showing the kerbside Purple bin
for the glass bottle and only THEN offer the user setup options. It must
NOT hallucinate a Pod-colour mapping or silently call set_pod_bin_preferences.
"""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessFalse, AssertCalledTool,
)
from tests import r_y_p_lg_fogo, make_user_data, make_target_args

name = "pod_bin_split_glass_no_prefs_kerbside_first"
description = (
    "User has a Pod system and a 4-bin split-recycling council (Red/Yellow/Purple "
    "glass/Lime Green FOGO). pod_bin_preferences is NOT set. Because there's no "
    "clean Pod-colour equivalent for the Purple glass bin, Pod must show the "
    "kerbside Purple bin for the glass bottle and then offer setup options — "
    "without hallucinating a Pod mapping or silently calling set_pod_bin_preferences."
)


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You have an empty glass wine bottle and want to know which bin it goes in. "
            "You have a Pod home bin system but you have NOT yet decided how you want to "
            "use each Pod bin colour — do NOT volunteer any preferences. Just ask about "
            "the bottle. If Pod offers you setup options or asks how you'd like to "
            "configure your Pod bins, respond neutrally with something like \"hmm, not "
            "sure yet, what do you suggest?\" — do NOT pick an option. Respond naturally "
            "and BRIEFLY, like a real user texting. Do NOT give recycling advice yourself. "
            "Call end_test ONLY once Pod has told you which bin to use AND offered at "
            "least one suggestion for how to handle glass via your Pod going forward — "
            "not before."
        ),
        first_message="Hi, I have an empty wine bottle — which bin does it go in?",
    )

    user_data = make_user_data(
        "pod-split-glass-noprefs",
        r_y_p_lg_fogo,
        pod_configuration="freestanding",
    )
    prompt_args, user_defined = make_target_args(user_data)

    target = TargetContext(
        session,
        agent_id=session.env("POD_AGENT_ID"),
        prompt_args=prompt_args,
        user_defined=user_defined,
    )

    run_conversation(sim, target, max_turns=20)

    target.check_all([
        AssertCalledTool("sort_item"),
        AssertCalledTool("show_bin", with_params={"show_reward": True, "points": 5}),
        AssessTrue(
            "Pod called show_bin with type kerbside and a Purple color for the glass "
            "bottle (NOT type pod with any colour)"
        ),
        AssessFalse(
            "Pod called show_bin with type pod for the glass bottle"
        ),
        AssessFalse(
            "Pod called set_pod_bin_preferences in this conversation (the user never "
            "picked a setup option, so prefs must not be saved)"
        ),
        AssessTrue(
            "After showing the kerbside bin for the glass bottle, Pod followed up by "
            "offering the user at least one option for how to handle glass via their "
            "Pod going forward (e.g. take it straight to the Purple kerbside bin, or "
            "use a Pod slot with a split-at-kerb instruction)"
        ),
        AssessTrue(
            "Pod gave a brief educational reason or fact about glass recycling (any "
            "practical or environmental reasoning counts)"
        ),
    ])
