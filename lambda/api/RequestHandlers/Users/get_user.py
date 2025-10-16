from pydantic import BaseModel
from Models.User import User
from Models.BinSystem import BinSystem, get_bin_system_by_id
from Models.Council import Council, get_council_by_id
from Models.HandlerPayload import HandlerPayload

class GetUserResponse(BaseModel):
    id: str
    email: str
    council: Council
    bin_system: BinSystem
    points: int
    created_at: int
    updated_at: int

def handler(payload: HandlerPayload) -> GetUserResponse:
    """
    Get the authenticated user with their council and bin_system resolved.
    """
    user: User = payload.user
    
    # Fetch the council
    council = get_council_by_id(user.council_id)
    if not council:
        raise Exception(f"Council not found for user: {user.council_id}", 404)
    
    # Fetch the bin system
    bin_system = get_bin_system_by_id(user.bin_system_id)
    if not bin_system:
        raise Exception(f"Bin system not found for user: {user.bin_system_id}", 404)
    
    # Return the user with resolved data
    return GetUserResponse(
        id=user.id,
        email=user.email,
        council=council,
        bin_system=bin_system,
        points=user.points,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
