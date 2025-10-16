from pydantic import BaseModel
from AWS.DynamoDB import get_item

COUNCILS_TABLE = "councils"
POSTCODE_TO_COUNCIL_TABLE = "postcode_to_council"

class Council(BaseModel):
    id: str
    mapId: str
    name: str

def get_council_by_id(council_id: str) -> Council | None:
    """
    Fetch a council by its ID.
    """
    council_data = get_item(
        table_name=COUNCILS_TABLE,
        primary_key_name="id",
        key=council_id
    )
    if not council_data:
        return None
    return Council(**council_data)

def get_councils_for_postcode(postcode: str) -> list[Council]:
    """
    Fetch councils associated with a given postcode.
    """
    response = get_item(
        table_name=POSTCODE_TO_COUNCIL_TABLE,
        primary_key_name="postcode",
        key=postcode
    )
    if not response or 'council_ids' not in response:
        return []
    
    council_ids = response['council_ids']
    councils = []
    for council_id in council_ids:
        council = get_council_by_id(council_id)
        if council:
            councils.append(council)
    
    return councils