from pydantic import BaseModel
from AWS.DynamoDB import get_item, put_item, get_all_items_by_index
from uuid import uuid4
from datetime import datetime

USERS_TABLE = "users"

class User(BaseModel):
    id: str
    email: str
    counsil_id: str
    bin_system_id: str
    points: float
    created_at: int
    updated_at: int

class CreateUserParams(BaseModel):
    email: str
    counsil_id: str
    bin_system_id: str

def create_user(params: CreateUserParams) -> User:
    """
    Create a new user with the provided parameters.
    """
    user_id = str(uuid4())
    now = int(datetime.now().timestamp())
    user = User(
        id=user_id,
        email=params.email,
        counsil_id=params.counsil_id,
        bin_system_id=params.bin_system_id,
        points=0.0,
        created_at=now,
        updated_at=now
    )
    put_item(
        table_name=USERS_TABLE,
        item=user.model_dump()
    )
    return user

def get_user(user_id: str) -> User | None:
    """
    Fetch a user by their ID.
    """
    response = get_item(
        table_name="Users",
        primary_key_name="id",
        key=user_id
    )
    if not response:
        return None
    return User(**response)

def get_user_with_email(email: str) -> User | None:
    """
    Fetch a user by their email
    """
    index_items = get_all_items_by_index(USERS_TABLE, "email", email)
    if not index_items:
        return None
    return User(**index_items[0])
    




    

    