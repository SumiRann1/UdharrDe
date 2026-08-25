from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import RedirectResponse
from auth.client import supabase
from supabase_auth._sync.gotrue_client import parse_user_response
from auth.deps import get_current_user, security, HTTPAuthorizationCredentials
from auth.schemas import (
    SignUpRequest, LoginRequest, VerifyOTPRequest, CompleteProfileRequest,
    UserResponse, AuthResponse, RefreshTokenRequest, ResetPasswordRequest, MessageResponse,
    OAuthSignInRequest, OAuthUrlResponse
)

auth_router = APIRouter(prefix = "/auth", tags=["auth"])

def build_user_response(user_data) -> UserResponse:
    return UserResponse(
        id=str(user_data.id),
        email=user_data.email,
        user_metadata=user_data.user_metadata or {},
        created_at=str(user_data.created_at) if user_data.created_at else None,
    )

@auth_router.get("/")
def index():
    return {"message": "Auth router is working"}

@auth_router.post("/signup", response_model=MessageResponse, summary="Initiates to create a new user")
def signup(request: SignUpRequest):
    try:
        supabase.auth.sign_up({
            "email": request.email,
            "password": request.password
        })
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))
    return MessageResponse(message="User registered successfully. Please check your email for the 6-digit OTP code.")

@auth_router.post("/verify-otp", response_model=AuthResponse, summary="Verifies the OTP sent to the user")
def verify_otp(request: VerifyOTPRequest):
    try:
        response = supabase.auth.verify_otp({
            "email": request.email,
            "token": request.token,
            "type": request.type 
        })
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))

    if response.session and response.session.access_token:
        try:
            supabase.auth._request("PUT", "user", jwt=response.session.access_token, body={
                "data": {"is_otp_verified": True}
            })
        except Exception:
            pass

    updated_metadata = {**(response.user.user_metadata or {}), "is_otp_verified": True}

    return AuthResponse(
        access_token=response.session.access_token,
        refresh_token=response.session.refresh_token,
        token_type=response.session.token_type,
        user=UserResponse(
            id=str(response.user.id),
            email=response.user.email,
            user_metadata=updated_metadata,
            created_at=str(response.user.created_at) if response.user.created_at else None
        )
    )
    
@auth_router.put("/complete-profile", response_model=UserResponse, summary="Completes the new user creation request")
def complete_profile(request: CompleteProfileRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_metadata = {
        "display_name": request.display_name,
        "name": request.display_name,
        "phone": request.phone,
        "is_otp_verified": True
    }     

    update_attrs = {"data": user_metadata}
    if request.phone:
        phone_val = request.phone.strip()
        if not phone_val.startswith("+"):
            phone_val = "+" + phone_val
        update_attrs["phone"] = phone_val

    try:
        raw_res = supabase.auth._request("PUT", "user", jwt=token, body=update_attrs)
    except Exception:
        raw_res = supabase.auth._request("PUT", "user", jwt=token, body={"data": user_metadata})

    parsed = parse_user_response(raw_res)

    return build_user_response(parsed.user)

@auth_router.post("/login", response_model=AuthResponse, summary="Log in an existing user")
def login(request: LoginRequest):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))
    return AuthResponse(
        access_token=response.session.access_token,
        refresh_token=response.session.refresh_token,
        token_type=response.session.token_type,
        user=UserResponse(
            id=str(response.user.id),
            email=response.user.email,
            user_metadata=response.user.user_metadata,
            created_at=str(response.user.created_at) if response.user.created_at else None
        )
    )

@auth_router.post("/logout", response_model=MessageResponse, summary="Sign out user session")
def logout(current_user: UserResponse = Depends(get_current_user)):
    supabase.auth.sign_out()
    return MessageResponse(message="User logged out successfully.")      
        
@auth_router.post("/refresh", response_model=AuthResponse, summary="Refresh access token")
def refresh_session(body: RefreshTokenRequest):
    res = supabase.auth.refresh_session(body.refresh_token)
    return AuthResponse(
        access_token=res.session.access_token,
        refresh_token=res.session.refresh_token,
        token_type=res.session.token_type or "bearer",
        user=build_user_response(res.user),
    )

@auth_router.post("/reset-password", response_model=MessageResponse, summary="Request password reset email")
def reset_password(body: ResetPasswordRequest):
    supabase.auth.reset_password_for_email(body.email)
    return MessageResponse(message="Password reset link sent to email if account exists.")


@auth_router.get("/me", response_model=UserResponse, summary="Get current user profile (Protecting Endpoints)")
def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@auth_router.get("/dashboard", response_model=UserResponse, summary="Protected user dashboard after login")
def dashboard(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@auth_router.post("/oauth/url", response_model=OAuthUrlResponse, summary="Generate OAuth authorization URL for sign-up/login")
def get_oauth_url(body: OAuthSignInRequest):
    try:
        options = {}
        if body.redirect_to:
            options["redirect_to"] = body.redirect_to

        res = supabase.auth.sign_in_with_oauth({
            "provider": body.provider,
            "options": options
        })
        return OAuthUrlResponse(url=res.url, provider=res.provider)
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@auth_router.get("/oauth/authorize", summary="Browser redirect to OAuth Provider authorization URL")
def authorize_oauth(
    provider: str = Query(..., description="OAuth provider, e.g. 'google', 'github', 'discord'"),
    redirect_to: Optional[str] = Query(None, description="Optional custom redirect URL after OAuth authentication")
):
    try:
        options = {}
        if redirect_to:
            options["redirect_to"] = redirect_to

        res = supabase.auth.sign_in_with_oauth({
            "provider": provider,
            "options": options
        })
        return RedirectResponse(url=res.url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@auth_router.get("/callback", response_model=AuthResponse, summary="Handle OAuth authorization code callback from Supabase")
def oauth_callback(
    code: Optional[str] = Query(None, description="Authorization code returned by Supabase OAuth redirect"),
    error: Optional[str] = Query(None, description="Error code if OAuth failed"),
    error_description: Optional[str] = Query(None, description="Error description if OAuth failed"),
    redirect_to: Optional[str] = Query(None, description="Original redirect URL if needed for PKCE exchange")
):
    """
    Callback endpoint that exchanges the authorization `code` received from Supabase/OAuth provider for a session.
    """
    if error or error_description:
        raise HTTPException(status_code=400, detail=error_description or error or "OAuth authentication failed")

    if not code:
        raise HTTPException(status_code=400, detail="Missing required 'code' parameter in callback")

    try:
        exchange_params = {"auth_code": code}
        if redirect_to:
            exchange_params["redirect_to"] = redirect_to

        res = supabase.auth.exchange_code_for_session(exchange_params)
        
        return AuthResponse(
            access_token=res.session.access_token,
            refresh_token=res.session.refresh_token,
            token_type=res.session.token_type or "bearer",
            user=build_user_response(res.user),
        )
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))