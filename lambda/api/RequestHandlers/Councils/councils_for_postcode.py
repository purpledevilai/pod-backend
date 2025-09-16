from Models.HandlerPayload import HandlerPayload
from Models import Council
from pydantic import BaseModel

class CouncilBasic(BaseModel):
    id: str
    name: str

class CouncilsForPostcodeResponse(BaseModel):
    councils: list[CouncilBasic]

def handler(payload: HandlerPayload ) -> CouncilsForPostcodeResponse:
    """
    Handle the request to get councils for a given postcode.
    This function retrieves councils associated with the provided postcode.

    Args:
        payload (HandlerPayload): The payload containing the lambda event and logger.

    Returns:
        CouncilsForPostcodeResponse: The response containing the list of councils.
    """
    # Get the logger from the payload
    logger = payload.logger

    # Extract postcode from path parameters
    postcode = payload.lambda_event.requestParameters.get('postcode')
    if not postcode:
        raise ValueError("Postcode is required in the path parameters")
    
    logger.info(f"Fetching councils for postcode: {postcode}")

    # Fetch councils for the given postcode
    councils = Council.get_councils_for_postcode(postcode)
    council_list = [CouncilBasic(id=c.id, name=c.name) for c in councils]

    logger.info(f"Found {len(council_list)} councils for postcode {postcode}")

    # Return the response
    return CouncilsForPostcodeResponse(councils=council_list)


    
