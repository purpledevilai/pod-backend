import json
import os
from pydantic import BaseModel
from Models.HandlerPayload import HandlerPayload
from Models import User
from Lib import JWT
from datetime import timedelta

class RefreshTokenBody(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    success: bool
    message: str
    access_token: str | None = None
    refresh_token: str | None = None

def handler(payload: HandlerPayload) -> RefreshTokenResponse:
    logger = payload.logger

    try:
        body = RefreshTokenBody(**json.loads(payload.lambda_event.body))
    except Exception:
        return RefreshTokenResponse(success=False, message="Invalid request body")

    refresh_token = body.refresh_token
    if not refresh_token:
        return RefreshTokenResponse(success=False, message="Missing refresh token")

    try:
        claims = JWT.extract_jwt_contents(os.getenv("JWT_SECRET"), refresh_token)
    except Exception:
        return RefreshTokenResponse(success=False, message="Invalid or expired refresh token")

    if claims.get("token_type") != "refresh_token":
        return RefreshTokenResponse(success=False, message="Invalid token type")

    user_id = claims.get("user_id")
    if not user_id:
        return RefreshTokenResponse(success=False, message="Malformed token: missing user_id")

    user = User.get_user_with_id(user_id)
    if not user:
        return RefreshTokenResponse(success=False, message="User not found")

    access_token = JWT.generate_jwt(os.getenv("JWT_SECRET"), {
        "user_id": user.id,
        "email": user.email,
        "token_type": "access_token",
    }, expires_in=timedelta(minutes=15))

    new_refresh_token = JWT.generate_jwt(os.getenv("JWT_SECRET"), {
        "user_id": user.id,
        "email": user.email,
        "token_type": "refresh_token",
    }, expires_in=timedelta(days=365))

    return RefreshTokenResponse(
        success=True,
        message="Token refreshed",
        access_token=access_token,
        refresh_token=new_refresh_token
    ) 