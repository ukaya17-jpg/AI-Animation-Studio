"""User registration and login HTTP endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_auth_service
from app.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from app.services.auth_service import (
    AuthService,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)

router = APIRouter(prefix="/auth")


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Register a new user account",
)
async def register(
    payload: UserRegisterRequest,
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> UserResponse:
    """Create a new account, rejecting an email already on file."""
    try:
        user = await service.register(email=payload.email, password=payload.password)
    except EmailAlreadyRegisteredError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Exchange email and password for a signed access token",
)
async def login(
    payload: UserLoginRequest,
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> TokenResponse:
    """Validate credentials and issue a bearer access token."""
    try:
        access_token = await service.login(email=payload.email, password=payload.password)
    except InvalidCredentialsError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    return TokenResponse(access_token=access_token)
