"""Pod already knows the user's name: should greet by name and never ask for it."""

import json

from ajentify_testing import (
    SimAgent, TargetContext, run_conversation,
    AssessTrue, AssessFalse, AssessScore, AssertCalledTool,
)
from tests import r_y_lg_fogo, make_user_data, make_target_args

name = "known_user_name"
description = (
    "When the user's name is already set in user_data, Pod should greet the user "
    "by their name (Jordan) and must not ask for the user's name during the conversation. "
    "Pod should also correctly classify the item the user asks about."
)


def run(session):
    user_data_dict = json.loads(make_user_data("known-name", r_y_lg_fogo))
    user_data_dict["name"] = "Jordan"
    user_data = json.dumps(user_data_dict)
    prompt_args, user_defined = make_target_args(user_data)

    sim = SimAgent(
        session,
        persona=(
            "You are Jordan. You want to know which bin to put a glass bottle in. "
            "Respond naturally. Call end_test ONLY once Pod has BOTH told you "
            "which bin AND told you how many points you earned for the "
            "classification — not before."
        ),
        first_message="Hi, I have a glass bottle — which bin does it go in?",
    )

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
        AssessTrue("Pod called show_bin with type kerbside and a Yellow color"),
        AssessTrue("Pod's first message included the user's name 'Jordan' (i.e. Pod said 'Jordan' as a greeting to the user)"),
        AssessTrue("Pod's opening message included the tagline 'Everything becomes something'"),
        AssessTrue("Pod used the word 'recycle' (or 'recycling') and never the word 'sort' or 'sorting' in any user-facing message"),
        AssessFalse("Pod asked the user for their name"),
        AssessTrue("Pod classified the glass bottle into the correct recycling bin"),
        AssessScore("Pod addressed the user in a warm and personalised way", min=0.5),
    ])
