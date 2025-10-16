from pydantic import BaseModel
from AWS.DynamoDB import get_item

BIN_SYSTEMS_TABLE = "bin_systems"
COUNCIL_TO_BIN_SYSTEM = "council_to_bin_system"

# Example BinSystem:
# {
#  "id": "99",
#  "bins": [
#   {
#    "id": "99-red-garbage",
#    "acceptsCardboard": false,
#    "acceptsContainers": false,
#    "acceptsFood": false,
#    "acceptsGarbage": true,
#    "acceptsGarden": false,
#    "acceptsGlass": false,
#    "acceptsSoftPlastics": true,
#    "appearance": "Red",
#    "extras": [
#    ],
#    "type": "Garbage"
#   },
#   {
#    "id": "99-blue-recycling",
#    "acceptsCardboard": true,
#    "acceptsContainers": true,
#    "acceptsFood": false,
#    "acceptsGarbage": false,
#    "acceptsGarden": false,
#    "acceptsGlass": true,
#    "acceptsSoftPlastics": false,
#    "appearance": "Blue",
#    "extras": [
#    ],
#    "type": "Recycling"
#   },
#   {
#    "id": "99-maroon-food-and-garden-waste",
#    "acceptsCardboard": false,
#    "acceptsContainers": false,
#    "acceptsFood": true,
#    "acceptsGarbage": false,
#    "acceptsGarden": true,
#    "acceptsGlass": false,
#    "acceptsSoftPlastics": false,
#    "appearance": "Maroon",
#    "extras": [
#    ],
#    "type": "Food and Garden Waste"
#   }
#  ]
# }

class Bin(BaseModel):
    id: str
    acceptsCardboard: bool
    acceptsContainers: bool
    acceptsFood: bool
    acceptsGarbage: bool
    acceptsGarden: bool
    acceptsGlass: bool
    acceptsSoftPlastics: bool
    appearance: str
    extras: list[str]
    type: str

class BinSystem(BaseModel):
    id: str
    bins: list[Bin]


# Example Council to BinSystem
# {
#  "council_id": "228",
#  "bin_systems": [
#   {
#    "bins": [
#     "2-green-garbage"
#    ],
#    "id": "2",
#    "is_default": true
#   },
#   {
#    "bins": [
#     "56-no-bin-system-no-kerbside-collection"
#    ],
#    "id": "56",
#    "is_default": false
#   }
#  ],
#  "council_name": "Shire of Mingenew"
# }
class SimpleBinSystem(BaseModel):
    id: str
    bins: list[str]
    is_default: bool

class CouncilToBinSystem(BaseModel):
    council_id: str
    bin_systems: list[SimpleBinSystem]
    council_name: str

def get_bin_system_by_id(bin_system_id: str) -> BinSystem | None:
    """
    Fetch a bin system by its ID.
    """
    bin_system_data = get_item(
        table_name=BIN_SYSTEMS_TABLE,
        primary_key_name="id",
        key=bin_system_id
    )
    if not bin_system_data:
        return None
    return BinSystem(**bin_system_data)

def get_bin_systems_for_council(council_id: str) -> list[BinSystem]:
    """
    Fetch bin systems associated with a given council ID.
    """
    response = get_item(
        table_name=COUNCIL_TO_BIN_SYSTEM,
        primary_key_name="council_id",
        key=council_id
    )
    if not response or 'bin_systems' not in response:
        return []
    
    council_to_bin_system = CouncilToBinSystem(**response)
    bin_systems = []
    for simple_bin_system in council_to_bin_system.bin_systems:
        bin_system = get_bin_system_by_id(simple_bin_system.id)
        if bin_system:
            bin_systems.append(bin_system)
    
    return bin_systems


