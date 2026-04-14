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
            "Respond naturally and call end_test once you get a clear bin classification."
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
        AssertCalledTool("show_bin"),
        AssessTrue("Pod called show_bin with type kerbside and a Yellow color"),
        AssessTrue("Pod greeted the user by their name Jordan"),
        AssessFalse("Pod asked the user for their name"),
        AssessTrue("Pod classified the glass bottle into the correct recycling bin"),
        AssessScore("Pod addressed the user in a warm and personalised way", min=0.5),
    ])
