from typing import Optional
from pydantic import BaseModel
from AWS.DynamoDB import get_item, put_item, update_item, delete_item, get_all_items_by_index
from uuid import uuid4
from datetime import datetime
from enum import Enum

from Models.Council import Council, get_council_by_id
from Models.BinSystem import BinSystem, get_bin_system_by_id

USERS_TABLE = "users"

class PodConfiguration(str, Enum):
    FREESTANDING = "freestanding"
    IN_DRAWER = "in_drawer"
    UNDER_SINK = "under_sink"
    NONE = "none"

class User(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    council_id: str
    bin_system_id: str
    pod_configuration: str = PodConfiguration.NONE.value
    points: int
    created_at: int
    updated_at: int

class UserResolved(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    council: Council
    bin_system: BinSystem
    pod_configuration: str
    points: int
    created_at: int
    updated_at: int


def resolve_user(user: User) -> UserResolved:
    council = get_council_by_id(user.council_id)
    if not council:
        raise Exception(f"Council not found: {user.council_id}", 404)

    bin_system = get_bin_system_by_id(user.bin_system_id)
    if not bin_system:
        raise Exception(f"Bin system not found: {user.bin_system_id}", 404)

    return UserResolved(
        id=user.id,
        email=user.email,
        name=user.name,
        council=council,
        bin_system=bin_system,
        pod_configuration=user.pod_configuration,
        points=user.points,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


class CreateUserParams(BaseModel):
    email: str
    council_id: str
    bin_system_id: str
    pod_configuration: str = PodConfiguration.NONE.value

def create_user(params: CreateUserParams) -> User:
    user_id = str(uuid4())
    now = int(datetime.now().timestamp())
    user = User(
        id=user_id,
        email=params.email,
        council_id=params.council_id,
        bin_system_id=params.bin_system_id,
        pod_configuration=params.pod_configuration,
        points=0,
        created_at=now,
        updated_at=now
    )
    put_item(
        table_name=USERS_TABLE,
        item=user.model_dump()
    )
    return user

def update_user(user_id: str, update_attributes: dict) -> User:
    update_attributes["updated_at"] = int(datetime.now().timestamp())
    updated = update_item(
        table_name=USERS_TABLE,
        primary_key_name="id",
        key=user_id,
        update_attributes=update_attributes
    )
    return User(**updated)

def get_user_with_email(email: str) -> User | None:
    """
    Fetch a user by their email
    """
    index_items = get_all_items_by_index(USERS_TABLE, "email", email)
    if not index_items:
        return None
    return User(**index_items[0])

def get_user_with_id(user_id: str) -> User | None:
    """
    Fetch a user by their ID
    """
    response = get_item(
        table_name=USERS_TABLE,
        primary_key_name="id",
        key=user_id
    )
    if not response:
        return None
    return User(**response)

def delete_user(user_id: str) -> None:
    delete_item(USERS_TABLE, "id", user_id)
