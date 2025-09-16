import json
import secrets
from Models.HandlerPayload import HandlerPayload
from Models import Challenge
from pydantic import BaseModel
from AWS import SES

class SendEmailVerificationBody(BaseModel):
    email: str

class SendEmailVerificationResponse(BaseModel):
    challenge_id: str

def handler(payload: HandlerPayload ) -> SendEmailVerificationResponse:
    """
    Handle the request to send an email verification code.
    This function generates a 6-digit code, creates a challenge with it, and sends the code to the user's email.
    
    Args:
        payload (HandlerPayload): The payload containing the lambda event and logger.
    
    Returns:
        SendEmailVerificationResponse: The response containing the challenge ID.
    """
    # Get the logger from the payload
    logger = payload.logger

    # Get the email from the body
    email = SendEmailVerificationBody(**json.loads(payload.lambda_event.body)).email
    logger.info(f"Request to verify {email}")

    # Validate the email format
    if not email or "@" not in email:
        raise ValueError("Invalid email address provided")

    # Create 6 digit code
    code = f"{secrets.randbelow(1_000_000):06d}"
    logger.info(f"Generated verification code: {code}")

    # Create a challenge with the code
    challenge = Challenge.create_challenge(params=Challenge.CreateChallengeParams(
        answer=code,
        metadata={"email": email}
    ))

    # Send the email with the code
    SES.send_email(
        from_email="purpledevilai@gmail.com",
        to_email=email,
        subject="Your Email Verification Code",
        body_text=f"Your verification code is: {code}",
        body_html=f"<p>Your verification code is: <strong>{code}</strong></p>"
    )
    logger.info(f"Sent verification code {code} to {email}")

    # Send the response
    return SendEmailVerificationResponse(challenge_id=challenge.id)


    
