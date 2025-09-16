import json
import re
from Models.HandlerPayload import HandlerPayload
from pydantic import BaseModel
from AWS.APIGateway import APIGatewayResponse, create_api_gateway_response
from AWS.Lambda import LambdaEvent
from AWS import CloudWatchLogs, SecretsManager
import RequestHandlers.Auth.send_email_verification
import RequestHandlers.Auth.verify_email
import RequestHandlers.Councils.councils_for_postcode
import RequestHandlers.BinSystems.bin_systems_for_council
import RequestHandlers.Users.create_user


# Handler registry
handler_registry = {
    "/send-email-verification": {
        "POST": {
            "handler": RequestHandlers.Auth.send_email_verification.handler,
            "public": True
        }
    },
    "/verify-email": {
        "POST": {
            "handler": RequestHandlers.Auth.verify_email.handler,
            "public": True
        }
    },
    "/councils-for-postcode/{postcode}": {
        "GET": {
            "handler": RequestHandlers.Councils.councils_for_postcode.handler,
            "public": True
        }
    },
    "/bin-systems-for-council/{council_id}": {
        "GET": {
            "handler": RequestHandlers.BinSystems.bin_systems_for_council.handler,
            "public": True
        }
    },
    "/create-user": {
        "POST": {
            "handler": RequestHandlers.Users.create_user.handler,
            "public": True
        }
    }
}

def match_route(request_path: str, method: str, handler_registry: dict) -> tuple:
    # Loop through routes to find the match
    for route, methods in handler_registry.items():
        # Replace placeholder variables with regex capture groups
        route_pattern = re.sub(
            r'\{(\w+)\}', 
            lambda m: rf'(?P<{m.group(1)}>.+)' if m.group(1) == 'link' else rf'(?P<{m.group(1)}>[^/]+)', 
            route
        )
        route_regex = f"^{route_pattern}$"
        match = re.match(route_regex, request_path)
        
        if match:
            handler_info = methods.get(method)
            if handler_info:
                # Extract named groups as parameters
                params = match.groupdict()
                handler = handler_info.get('handler')
                is_public = handler_info.get('public', False)  # Default to False if 'public' key is missing
                return_type = handler_info.get('return_type', 'application/json')  # Default to 'json' if 'return_type' key is missing
                return handler, params, is_public, return_type
    
    return None, None, None, None

def lambda_handler(event: dict, context) -> APIGatewayResponse:

    # Logger
    logger = CloudWatchLogs.get_logger(log_level="INFO")

    # Populate env with secret values
    SecretsManager.load_secrets_from_arn()

    try:
        # Create a LambdaEvent object from the event
        lambda_event = LambdaEvent(**event)
        logger.info(f"Request Event: {json.dumps(lambda_event.model_dump())}")

        # Get the request details
        request_path: str = lambda_event.path
        request_method: str = lambda_event.httpMethod
        logger.info(f"{request_method} {request_path}")

        # Get the handler for the request
        handler, request_params, is_public, return_type = match_route(request_path, request_method, handler_registry)
        if not handler:
            raise Exception("Invalid request path", 404)
        lambda_event.requestParameters = request_params
        logger.info(f"Request Parameters: {json.dumps(lambda_event.requestParameters)}")

        # If not public check for access token
        if (not is_public):
            access_token = lambda_event.headers.get("Authorization")
            if (access_token == None):
                raise Exception("No authentication token provided")
            # TODO: validate the access token. 
            
        # Call the handler
        response: BaseModel = handler(HandlerPayload(
            lambda_event=lambda_event,
            logger=logger
        ))
        
        # Get return content based on return type
        return_result = None
        if (return_type == 'application/json'):
            return_result = response.model_dump()
            logger.info(f"Return result: {json.dumps(return_result)}")
        else:
            return_result = response
            logger.info(f"Return result: {return_result}")

        # Return the response 
        return create_api_gateway_response(
            200,
            return_result,
            return_type
        )
            

    # Return any errors   
    except Exception as e:
        logger.error(str(e))
        error, code = e.args if len(e.args) == 2 else (e, 500)
        return create_api_gateway_response(
            code,
            { 'error': str(error) },
            'application/json'
        )