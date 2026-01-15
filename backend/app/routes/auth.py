import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, get_current_user
from app.core.config import get_settings
from app.core.db import get_session
from app.services.lichess import exchange_code, generate_pkce, get_account
from app.models.models import User

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.get("/login")
async def login_via_lichess() -> RedirectResponse:
    """Initiate OAuth login flow with Lichess."""
    code_verifier, code_challenge = generate_pkce()
    state = secrets.token_urlsafe(32)
    
    params = {
        "response_type": "code",
        "client_id": settings.lichess_client_id,
        "redirect_uri": str(settings.lichess_redirect_uri),
        "scope": "preference:read email:read",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    url = f"https://lichess.org/oauth?{urlencode(params)}"
    
    response = RedirectResponse(url)
    response.set_cookie(
        key="oauth_verifier",
        value=f"{state}:{code_verifier}",
        httponly=True,
        secure=settings.app_env != "dev",
        samesite="lax",
        max_age=600,
    )
    return response


@router.get("/callback")
async def auth_callback(
    request: Request,
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """Handle OAuth callback from Lichess."""
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error} - {error_description}")

    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state parameter")

    oauth_verifier = request.cookies.get("oauth_verifier")
    if not oauth_verifier or ":" not in oauth_verifier:
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    stored_state, code_verifier = oauth_verifier.split(":", 1)
    if stored_state != state:
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    token = await exchange_code(code, code_verifier)
    account = await get_account(token.access_token)
    
    lichess_id = account.get("id")
    username = account.get("username")

    result = await session.execute(select(User).where(User.lichess_id == lichess_id))
    user = result.scalars().first()
    
    expires_at = None
    if token.expires_in:
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=token.expires_in)

    if user:
        user.access_token = token.access_token
        user.refresh_token = token.refresh_token
        user.token_type = token.token_type
        user.scope = token.scope
        user.expires_at = expires_at
        user.updated_at = datetime.now(timezone.utc)
    else:
        user = User(
            lichess_id=lichess_id,
            username=username,
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            token_type=token.token_type,
            scope=token.scope,
            expires_at=expires_at,
        )
        session.add(user)
    
    await session.commit()
    await session.refresh(user)

    jwt_token = create_access_token(user.id, user.username)

    frontend_base = settings.redirect_url.rstrip("/")
    response = RedirectResponse(url=f"{frontend_base}/")
    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,
        secure=settings.app_env != "dev",
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    response.delete_cookie(key="oauth_verifier")
    return response


@router.post("/logout")
async def logout(response: Response):
    """Logout user."""
    response.delete_cookie(key="access_token")
    return {"message": "Logged out"}


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    """Get current user info."""
    return {
        "id": user.id,
        "username": user.username,
        "lichess_id": user.lichess_id,
    }
