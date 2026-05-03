"""Pod bin system — Sydney-shape council, no prefs, kerbside-first behaviour for food.

User has a Pod system and a 4-bin Sydney-shape council (Red Garbage,
Yellow Recycling, Green Garden Waste, Maroon Food Waste). pod_bin_preferences
is NOT set.

Because there's no clean Pod-colour equivalent for the Maroon Food Waste
bin, Pod must default to showing the kerbside Maroon bin for the food
scraps and only THEN offer the user setup options. It must NOT hallucinate
a Pod-colour mapping (especially not "white = food" which is a separate
soft-plastics slot) or silently call set_pod_bin_preferences.
"""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessFalse, AssertCalledTool,
)
from tests import r_y_g_m_food, make_user_data, make_target_args

name = "pod_bin_sydney_food_no_prefs_kerbside_first"
description = (
    "User has a Pod system and a 4-bin Sydney-shape council (Red/Yellow/Green "
    "Garden/Maroon Food). pod_bin_preferences is NOT set. Because there's no "
    "clean Pod-colour equivalent for the Maroon food bin, Pod must show the "
    "kerbside Maroon bin for the spaghetti and then offer setup options — "
    "without hallucinating a Pod mapping or silently calling set_pod_bin_preferences."
)


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You have some leftover spaghetti and want to know which bin it goes in. "
            "You have a Pod home bin system but you have NOT yet decided how you want "
            "to use each Pod bin colour — do NOT volunteer any preferences. Just ask "
            "about the spaghetti. If Pod offers you setup options or asks how you'd "
            "like to configure your Pod bins, respond neutrally with something like "
            "\"hmm, not sure yet, what do you suggest?\" — do NOT pick an option. "
            "Respond naturally and BRIEFLY, like a real user texting. Do NOT give "
            "recycling advice yourself. Call end_test ONLY once Pod has told you "
            "which bin to use AND offered at least one suggestion for how to handle "
            "food via your Pod going forward — not before."
        ),
        first_message="Hey, I've got some leftover spaghetti — which bin does it go in?",
    )

    user_data = make_user_data(
        "pod-sydney-food-noprefs",
        r_y_g_m_food,
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
            "Pod called show_bin with type kerbside and a Maroon color for the "
            "spaghetti (NOT type pod with any colour)"
        ),
        AssessFalse(
            "Pod called show_bin with type pod for the spaghetti (e.g. white, green, "
            "or any other Pod colour)"
        ),
        AssessFalse(
            "Pod called set_pod_bin_preferences in this conversation (the user never "
            "picked a setup option, so prefs must not be saved)"
        ),
        AssessTrue(
            "After showing the kerbside Maroon bin for the spaghetti, Pod followed up "
            "by offering the user at least one option for how to handle food via their "
            "Pod going forward (e.g. take it straight to the Maroon kerbside bin, or "
            "use a Pod slot dedicated to food)"
        ),
    ])
