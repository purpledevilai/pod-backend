from pydantic import BaseModel
from AWS.DynamoDB import get_item, put_item
from uuid import uuid4
from datetime import datetime

CHALLENGES_TABLE = "challenges"

class Challenge(BaseModel):
    id: str
    answer: str
    metadata: dict | None = None
    verified: bool
    expiry: int
    attempts_remaining: int
    created_at: int
    updated_at: int

class CreateChallengeParams(BaseModel):
    answer: str
    metadata: dict | None = None
    ttl: int = 900  # Default to 15 minutes in seconds
    attempts_remaining: int = 3  # Default to 3 attempts

def create_challenge(params: CreateChallengeParams) -> Challenge:
    """
    Create a new challenge given it's answer
    """
    challenge_id = str(uuid4())
    now = int(datetime.now().timestamp())
    challenge = Challenge(
        id=challenge_id,
        answer=params.answer,
        metadata=params.metadata,
        verified=False,
        expiry=now + params.ttl,
        attempts_remaining=params.attempts_remaining,
        created_at=now,
        updated_at=now
    )
    put_item(
        table_name=CHALLENGES_TABLE,
        item=challenge.model_dump()
    )
    return challenge

def get_challenge(challenge_id) -> Challenge | None:
    """
    Fetch a challenge by its ID
    """
    response = get_item(
        table_name=CHALLENGES_TABLE,
        primary_key_name="id",
        key=challenge_id
    )
    if not response:
        return None
    return Challenge(**response)

def update_challenge(challenge: Challenge) -> Challenge:
    """
    Update an existing challenge
    """
    challenge.updated_at = int(datetime.now().timestamp())
    put_item(
        table_name=CHALLENGES_TABLE,
        item=challenge.model_dump()
    )
    return challenge