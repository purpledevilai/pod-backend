from Models.HandlerPayload import HandlerPayload
from Models import BinSystem
from pydantic import BaseModel


class BinSystemsForCouncilResponse(BaseModel):
    bin_systems: list[BinSystem.BinSystem]

def handler(payload: HandlerPayload ) -> BinSystemsForCouncilResponse:
    """
    Handle the request to get bin systems for a given council ID.
    This function retrieves bin systems associated with the provided council ID.

    Args:
        payload (HandlerPayload): The payload containing the lambda event and logger.

    Returns:
        BinSystemsForCouncilResponse: The response containing the list of bin systems.
    """
    # Get the logger from the payload
    logger = payload.logger

    # Extract council_id from path parameters
    council_id = payload.lambda_event.requestParameters.get('council_id')
    if not council_id:
        raise ValueError("Council ID is required in the path parameters")
    
    logger.info(f"Fetching bin systems for council ID: {council_id}")

    # Fetch bin systems for the given council ID
    bin_systems = BinSystem.get_bin_systems_for_council(council_id)

    logger.info(f"Found {len(bin_systems)} bin systems for council ID {council_id}")

    # Return the response
    return BinSystemsForCouncilResponse(bin_systems=bin_systems)


    
