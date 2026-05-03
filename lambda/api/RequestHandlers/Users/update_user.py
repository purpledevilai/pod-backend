import json
from pydantic import BaseModel
from typing import Optional
from Models.HandlerPayload import HandlerPayload
from Models.User import User, PodConfiguration, update_user as update_user_db
from Models.BinSystem import BinSystem, get_bin_system_by_id
from Models.Council import Council, get_council_by_id


class UpdateUserBody(BaseModel):
    council_id: Optional[str] = None
    bin_system_id: Optional[str] = None
    pod_configuration: Optional[str] = None


class UpdateUserResponse(BaseModel):
    id: str
    email: str
    council: Council
    bin_system: BinSystem
    pod_configuration: str
    points: int
    created_at: int
    updated_at: int


def handler(payload: HandlerPayload) -> UpdateUserResponse:
    logger = payload.logger
    user: User = payload.user

    body = UpdateUserBody(**json.loads(payload.lambda_event.body))

    update_attrs = {}

    if body.council_id is not None:
        council = get_council_by_id(body.council_id)
        if not council:
            raise Exception(f"Council not found: {body.council_id}", 404)
        update_attrs["council_id"] = body.council_id

    if body.bin_system_id is not None:
        bin_system = get_bin_system_by_id(body.bin_system_id)
        if not bin_system:
            raise Exception(f"Bin system not found: {body.bin_system_id}", 404)
        update_attrs["bin_system_id"] = body.bin_system_id

        if body.bin_system_id != user.bin_system_id:
            update_attrs["pod_bin_preferences"] = None

    if body.pod_configuration is not None:
        valid_values = [e.value for e in PodConfiguration]
        if body.pod_configuration not in valid_values:
            raise Exception(f"Invalid pod_configuration: {body.pod_configuration}. Must be one of {valid_values}", 400)
        update_attrs["pod_configuration"] = body.pod_configuration

    if not update_attrs:
        raise Exception("No fields to update", 400)

    logger.info(f"Updating user {user.id} with: {json.dumps(update_attrs)}")
    updated_user = update_user_db(user.id, update_attrs)

    council = get_council_by_id(updated_user.council_id)
    if not council:
        raise Exception(f"Council not found for user: {updated_user.council_id}", 404)

    bin_system = get_bin_system_by_id(updated_user.bin_system_id)
    if not bin_system:
        raise Exception(f"Bin system not found for user: {updated_user.bin_system_id}", 404)

    return UpdateUserResponse(
        id=updated_user.id,
        email=updated_user.email,
        council=council,
        bin_system=bin_system,
        pod_configuration=updated_user.pod_configuration,
        points=updated_user.points,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
    )
