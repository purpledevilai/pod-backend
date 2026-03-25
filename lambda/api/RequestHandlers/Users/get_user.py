from Models.User import UserResolved, resolve_user
from Models.HandlerPayload import HandlerPayload


def handler(payload: HandlerPayload) -> UserResolved:
    """
    Get the authenticated user with their council and bin_system resolved.
    """
    return resolve_user(payload.user)
