import json
import re
import os
from Models.HandlerPayload import HandlerPayload
from Models import User
from Lib import JWT
from pydantic import BaseModel
from AWS.APIGateway import APIGatewayResponse, create_api_gateway_response
from AWS.Lambda import LambdaEvent
from AWS import CloudWatchLogs, SecretsManager
import RequestHandlers.Auth.send_email_verification
import RequestHandlers.Auth.verify_email
import RequestHandlers.Auth.refresh_token
import RequestHandlers.Councils.councils_for_postcode
import RequestHandlers.BinSystems.bin_systems_for_council
import RequestHandlers.Users.create_user
import RequestHandlers.Users.get_user
import RequestHandlers.Users.update_user
import RequestHandlers.Agent.create_agent_context
import RequestHandlers.Users.set_user_name


# Load secrets
SecretsManager.load_secrets_from_arn()

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
    "/refresh-token": {
        "POST": {
            "handler": RequestHandlers.Auth.refresh_token.handler,
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
    "/create-account": {
        "POST": {
            "handler": RequestHandlers.Users.create_user.handler,
            "public": True
        }
    },
    "/user": {
        "GET": {
            "handler": RequestHandlers.Users.get_user.handler,
            "public": False
        },
        "PATCH": {
            "handler": RequestHandlers.Users.update_user.handler,
            "public": False
        }
    },
    "/create-agent-context": {
        "POST": {
            "handler": RequestHandlers.Agent.create_agent_context.handler,
            "public": False
        }
    },
    "/set-user-name": {
        "POST": {
            "handler": RequestHandlers.Users.set_user_name.handler,
            "public": False
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

        # Create the HandlerPayload
        payload = HandlerPayload(
            lambda_event=lambda_event,
            logger=logger
        )

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
            access_token = access_token.replace("Bearer ", "")
            try:
                token_contents = JWT.extract_jwt_contents(os.getenv("JWT_SECRET"), access_token)
                # Enforce access token type
                if token_contents.get("token_type") != "access_token":
                    raise Exception("Invalid token type for this endpoint", 401)
                user_id = token_contents.get("user_id")
                user = User.get_user_with_id(user_id)
                if not user:
                    raise Exception("User not found", 401)
                payload.user = user
                logger.info(f"Authenticated user {user.email} ({user.id})")
            except Exception as e:
                logger.error(f"Invalid or expired authentication token: {e}")
                raise Exception("Invalid or expired authentication token", 401)
            
        # Call the handler
        response: BaseModel = handler(payload)
        
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