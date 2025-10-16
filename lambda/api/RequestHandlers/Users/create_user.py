import json
import os
from Models.HandlerPayload import HandlerPayload
from Models import User
from pydantic import BaseModel
from Lib import JWT
from datetime import timedelta


class CreateUserBody(BaseModel):
    create_account_token: str
    council_id: str
    bin_system_id: str

class CreateUserResponse(BaseModel):
    user: User.User
    access_token: str
    refresh_token: str

def handler(payload: HandlerPayload ) -> CreateUserResponse:
    """
    Handle the request to create a new user.
    This function creates a new user with the provided create account token, council ID, and bin system ID.

    Args:
        payload (HandlerPayload): The payload containing the lambda event and logger.

    Returns:
        CreateUserResponse: The response containing the created user and authentication tokens.
    """
    # Get the logger from the payload
    logger = payload.logger

    # Parse the body to get create account token, council ID, and bin system ID
    body = CreateUserBody(**json.loads(payload.lambda_event.body))
    logger.info(f"Creating user with council ID {body.council_id} and bin system ID {body.bin_system_id}")

    # Verify the create account token
    try:
        token_data = JWT.extract_jwt_contents(os.environ["JWT_SECRET"], body.create_account_token)
        email = token_data.get("verified_email")
        if not email:
            raise ValueError("Invalid token: email not found")
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise ValueError("Invalid create account token")

    # Check if a user with the same email already exists
    existing_user = User.get_user_with_email(email)
    if existing_user:
        raise ValueError("A user with this email already exists")

    # Create the new user
    user_params = User.CreateUserParams(
        email=email,
        council_id=body.council_id,
        bin_system_id=body.bin_system_id
    )
    new_user = User.create_user(user_params)
    logger.info(f"User created with ID {new_user.id}")

    # Generate authentication and refresh tokens
    access_token = JWT.generate_jwt(os.getenv("JWT_SECRET"), {
        "user_id": new_user.id,
        "email": new_user.email,
        "token_type": "access_token",
    }, expires_in=timedelta(hours=8))

    refresh_token = JWT.generate_jwt(os.getenv("JWT_SECRET"), {
        "user_id": new_user.id,
        "email": new_user.email,
        "token_type": "refresh_token",
    }, expires_in=timedelta(days=365))

    # Return the response
    return CreateUserResponse(
        user=new_user,
        access_token=access_token,
        refresh_token=refresh_token
    )