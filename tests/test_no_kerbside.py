"""No kerbside collection: user has no bin system at all."""

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessScore, AssertNotCalledTool,
)
from tests import no_bin_system, make_user_data, make_target_args

name = "no_kerbside"
description = (
    "A user whose council has no kerbside bin collection asks where to put a cardboard box. "
    "The only 'bin' is 'No Kerbside Collection' with appearance 'No Bin System' and all "
    "accepts flags set to true. Pod should recognise this unusual situation and guide the "
    "user appropriately — ideally noting that they don't have standard bins and may need "
    "to take items to a transfer station or recycling centre."
)


def run(session):
    sim = SimAgent(
        session,
        persona=(
            "You are a person who has a cardboard box to get rid of but "
            "you're not sure what to do with it. Respond naturally and call "
            "end_test once you get a clear answer or recommendation."
        ),
        first_message="Hi, I have a cardboard box to get rid of — what should I do with it?",
    )

    user_data = make_user_data("nokerbside", no_bin_system)
    prompt_args, user_defined = make_target_args(user_data)

    target = TargetContext(
        session,
        agent_id=session.env("POD_AGENT_ID"),
        prompt_args=prompt_args,
        user_defined=user_defined,
    )

    run_conversation(sim, target, max_turns=15)

    target.check_all([
        AssertNotCalledTool("show_bin"),
        AssessTrue("Pod acknowledged that the user has no standard kerbside bin collection"),
        AssessTrue(
            "Pod suggested an alternative such as a transfer station, recycling centre, "
            "or council drop-off for the cardboard"
        ),
        AssessScore("The sim user behaved as a real user (stated their item, asked for help) rather than acting like an assistant", min=0.7),
    ])
