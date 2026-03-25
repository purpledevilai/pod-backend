import json
from pydantic import BaseModel
from Models.HandlerPayload import HandlerPayload
from Models.User import update_user


class SetUserNameBody(BaseModel):
    name: str


class SetUserNameResponse(BaseModel):
    name: str


def handler(payload: HandlerPayload) -> SetUserNameResponse:
    user = payload.user
    body = SetUserNameBody(**json.loads(payload.lambda_event.body))

    update_user(user.id, {"name": body.name})

    return SetUserNameResponse(name=body.name)
