import json
from pydantic import BaseModel
from Models.HandlerPayload import HandlerPayload
from Models.User import increment_user_points


class RewardPointsBody(BaseModel):
    points: int


class RewardPointsResponse(BaseModel):
    points: int


def handler(payload: HandlerPayload) -> RewardPointsResponse:
    logger = payload.logger
    user = payload.user

    body = RewardPointsBody(**json.loads(payload.lambda_event.body))

    if body.points <= 0:
        raise Exception("points must be a positive integer", 400)

    new_total = increment_user_points(user.id, body.points)
    logger.info(f"Awarded {body.points} points to user {user.id}; new total {new_total}")

    return RewardPointsResponse(points=new_total)
