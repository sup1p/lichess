import base64
import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import get_settings
from app.schemas.schemas import TokenPayload


settings = get_settings()

LICHESS_BASE = "https://lichess.org"
TOKEN_URL = f"{LICHESS_BASE}/api/token"
ACCOUNT_URL = f"{LICHESS_BASE}/api/account"
GAMES_URL_TEMPLATE = f"{LICHESS_BASE}/api/games/user/{{username}}"


def generate_pkce() -> tuple[str, str]:
    """Generate PKCE code_verifier and code_challenge."""
    code_verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return code_verifier, code_challenge


async def exchange_code(code: str, code_verifier: str) -> TokenPayload:
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.lichess_client_id,
        "code": code,
        "redirect_uri": str(settings.lichess_redirect_uri),
        "code_verifier": code_verifier,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(TOKEN_URL, data=data)
        resp.raise_for_status()
        payload = resp.json()
    expires_in = payload.get("expires_in")
    return TokenPayload(
        access_token=payload["access_token"],
        token_type=payload.get("token_type", "Bearer"),
        refresh_token=payload.get("refresh_token"),
        expires_in=expires_in,
        scope=payload.get("scope"),
    )


async def refresh_access_token(refresh_token_value: str) -> TokenPayload:
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token_value,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(TOKEN_URL, data=data)
        resp.raise_for_status()
        payload = resp.json()
    return TokenPayload(
        access_token=payload["access_token"],
        token_type=payload.get("token_type", "Bearer"),
        refresh_token=payload.get("refresh_token", refresh_token_value),
        expires_in=payload.get("expires_in"),
        scope=payload.get("scope"),
    )


async def get_account(access_token: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(ACCOUNT_URL, headers={"Authorization": f"Bearer {access_token}"})
        resp.raise_for_status()
        return resp.json()


async def get_games(
    username: str,
    access_token: str,
    max_games: int = 50,
    perf_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> List[Dict[str, Any]]:
    """Fetch games from Lichess API. Returns a list of game objects.
    
    Note: Lichess API returns NDJSON (newline-delimited JSON), not a JSON array.
    """
    params: Dict[str, Any] = {
        "max": max_games,
        "pgnInJson": "true",
    }
    if perf_type:
        params["perfType"] = perf_type
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/x-ndjson",
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            GAMES_URL_TEMPLATE.format(username=username),
            params=params,
            headers=headers,
        )
        resp.raise_for_status()
        
        # Parse NDJSON (one JSON object per line)
        games = []
        for line in resp.text.strip().split("\n"):
            if line:
                games.append(json.loads(line))
        return games
