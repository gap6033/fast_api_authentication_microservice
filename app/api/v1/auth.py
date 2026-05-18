from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from app.schemas.user import UserCreateRequest, UserCreateResponse, UserLoginRequest, UserLoginResponse
from app.schemas.token import TokenLoginResponse
from fastapi.responses import JSONResponse
from app.services.auth_service import AuthService
from app.exceptions.user_exceptions import UserExistsException
from app.dependencies.dependencies import get_auth_service
from app.exceptions.user_exceptions import UserExistsException
from app.exceptions.auth_exceptions import InvalidCredentialsException
import jwt
from app.dependencies.dependencies import oauth2_scheme


router = APIRouter()

@router.post("/users/register", response_model=UserCreateResponse)
def register(user: UserCreateRequest, auth_service: AuthService = Depends(get_auth_service)) -> UserCreateResponse:
    try:
        return auth_service.register(user)
    except UserExistsException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{user.email} Email already registered")
    
    
@router.post("/users/login", response_model=UserLoginResponse)
def login(user: UserLoginRequest, response: Response, auth_service: AuthService = Depends(get_auth_service)) -> UserLoginResponse:
    try:
        token_response: TokenLoginResponse = auth_service.login(user)
    except InvalidCredentialsException:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    response.set_cookie(
            key="refresh_token",
            value=token_response.refresh_token,
            httponly=True,
            secure=True,       # Use HTTPS in production
            samesite="strict",
            max_age=token_response.refresh_token_expiry,
            path="/v1/auth"
        )
    return UserLoginResponse(access_token=token_response.access_token, token_type=token_response.token_type)

@router.post("/users/logout")
def logout(response: Response, access_token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends(get_auth_service), refresh_token: str = Cookie(None)):
    try:
        auth_service.logout(access_token, refresh_token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    response.delete_cookie("refresh_token", path="/v1/auth")
    return JSONResponse({"message": "Successfully logged out user"})

@router.delete("/users/me")
def delete_user(response: Response, access_token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends(get_auth_service), refresh_token: str = Cookie(None)):
    """
    Delete the currently authenticated user.
    Requires authentication.
    """
    try:
        auth_service.delete_user(access_token, refresh_token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        if isinstance(e, jwt.ExpiredSignatureError):
            print("expired access token", access_token)
        else:
            print("invalid access token", access_token)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    response.delete_cookie("refresh_token", path="/v1/auth")
    return JSONResponse({
            "message": f"User successfully deleted",
            "status": "success"
        })

@router.post("/refresh")
def refresh_token(access_token = Depends(oauth2_scheme), auth_service: AuthService = Depends(get_auth_service), refresh_token: str = Cookie(None)):
    access_token = auth_service.refresh_token(access_token, refresh_token)
    return JSONResponse({"access_token": access_token, "token_type": "bearer"})