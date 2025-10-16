from datetime import datetime
import os
import json
from Models.HandlerPayload import HandlerPayload
from Models import Challenge, User
from pydantic import BaseModel
from Lib import JWT
from datetime import timedelta

class VerifyEmailBody(BaseModel):
    challenge_id: str
    answer: str

class VerifyEmailResponse(BaseModel):
    success: bool
    message: str
    create_account_token: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None

def handler(payload: HandlerPayload ) -> VerifyEmailResponse:
    """Handle the request to verify an email using a challenge.
This function checks the provided answer against the challenge's answer,
and if correct, marks the challenge as verified and returns a success response.

Args:
    payload (HandlerPayload): The payload containing the lambda event and logger.

Returns:
    VerifyEmailResponse: The response indicating success or failure of verification.
    """
    # Get the logger from the payload
    logger = payload.logger

    # Parse the body to get challenge ID and answer
    body = VerifyEmailBody(**json.loads(payload.lambda_event.body))
    logger.info(f"Verifying challenge {body.challenge_id} with answer {body.answer}")

    # Fetch the challenge
    challenge = Challenge.get_challenge(body.challenge_id)
    if not challenge:
        raise ValueError("Challenge not found")
    
    # Check if the challenge is expired
    if challenge.expiry < int(datetime.now().timestamp()):
        return VerifyEmailResponse(
            success=False,
            message="Verification code has expired. Please send a new code.",
        )

    # Check if the challenge is already verified
    if challenge.verified:
        return VerifyEmailResponse(
            success=False,
            message="This verification code has already been used. Please send a new code.",
        )
    
    # Decrement the attempts remaining
    challenge.attempts_remaining -= 1
    Challenge.update_challenge(challenge)
    
    # Check if the challenge has remaining attempts
    if challenge.attempts_remaining < 0:
        return VerifyEmailResponse(
            success=False,
            message="No attempts remaining for this verification code. Please send a new code.",
        )

    # Check if the answer is correct
    if challenge.answer != body.answer:
        return VerifyEmailResponse(
            success=False,
            message="Incorrect verification code provided.",
        )
    
    # Mark the challenge as verified
    challenge.verified = True
    Challenge.update_challenge(challenge)

    # Get the email from the challenge
    email = challenge.metadata["email"]

    # See if user exists
    user = User.get_user_with_email(email)

    if not user:
        # Generate the jwt token that will allow user to create an account
        create_account_token = JWT.generate_jwt(os.getenv("JWT_SECRET"), {
            "verified_email": email
        })
        return VerifyEmailResponse(
            success=True,
            message="Email verified successfully. Please create an account.",
            create_account_token=create_account_token
        )
    
    # Generate the access and refresh tokens for the user
    access_token = JWT.generate_jwt(os.getenv("JWT_SECRET"), {
        "user_id": user.id,
        "email": user.email,
        "token_type": "access_token",
    }, expires_in=timedelta(minutes=15))

    refresh_token = JWT.generate_jwt(os.getenv("JWT_SECRET"), {
        "user_id": user.id,
        "email": user.email,
        "token_type": "refresh_token",
    }, expires_in=timedelta(days=365))

    return VerifyEmailResponse(
        success=True,
        message="Email verified successfully.",
        access_token=access_token,
        refresh_token=refresh_token
    )
