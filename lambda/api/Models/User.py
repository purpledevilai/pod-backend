from pydantic import BaseModel
from AWS.DynamoDB import get_item, put_item, update_item, get_all_items_by_index
from uuid import uuid4
from datetime import datetime
from enum import Enum

USERS_TABLE = "users"

class PodConfiguration(str, Enum):
    FREESTANDING = "freestanding"
    IN_DRAWER = "in_drawer"
    UNDER_SINK = "under_sink"
    NONE = "none"

class User(BaseModel):
    id: str
    email: str
    council_id: str
    bin_system_id: str
    pod_configuration: str = PodConfiguration.NONE.value
    points: int
    created_at: int
    updated_at: int

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
    




    

    