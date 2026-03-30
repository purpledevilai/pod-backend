import json
from pydantic import BaseModel
from Models.HandlerPayload import HandlerPayload
from Models.User import update_user


class SetPodBinPreferencesBody(BaseModel):
    pod_bin_preferences: dict


class SetPodBinPreferencesResponse(BaseModel):
    pod_bin_preferences: dict


def handler(payload: HandlerPayload) -> SetPodBinPreferencesResponse:
    user = payload.user
    body = SetPodBinPreferencesBody(**json.loads(payload.lambda_event.body))

    update_user(user.id, {"pod_bin_preferences": body.pod_bin_preferences})

    return SetPodBinPreferencesResponse(pod_bin_preferences=body.pod_bin_preferences)
