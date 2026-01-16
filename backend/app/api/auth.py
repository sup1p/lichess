import logging
import secrets
from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, get_current_user
from app.core.config import get_settings
from app.core.db import get_session
from app.services.lichess import exchange_code, generate_pkce, get_account
from app.models.models import User
from app.services import crud
from app.tasks import sync_all_user_games

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.get("/login")
async def login_via_lichess() -> RedirectResponse:
    """Initiate OAuth login flow with Lichess."""
    logger.info("Initiating OAuth login flow")
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
        secure=False,
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
    logger.info(f"OAuth callback received for user: {username}")

    # Get or create user
    user = await crud.get_user_by_lichess_id(session, lichess_id)
    
    if user:
        user = await crud.update_user_tokens(session, user, username, token)
        is_new_user = False
        logger.info(f"Existing user logged in: {username}")
    else:
        user = await crud.create_user(session, lichess_id, username, token)
        is_new_user = True
        logger.info(f"New user created: {username}")
    
    await session.commit()
    await session.refresh(user)
    
    # Trigger background task to sync all games for new users
    if is_new_user:
        logger.info(f"Triggering sync_all_user_games for user_id={user.id}")
        sync_all_user_games.delay(user.id)

    jwt_token = create_access_token(user.id, user.username)

    frontend_base = settings.redirect_url.rstrip("/")
    response = RedirectResponse(url=f"{frontend_base}/")
    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,
        secure=False,
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
