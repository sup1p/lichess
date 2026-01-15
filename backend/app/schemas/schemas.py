from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class TokenPayload(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    scope: Optional[str] = None


class UserCreate(BaseModel):
    lichess_id: str
    username: str
    token: TokenPayload


class UserPublic(BaseModel):
    username: str
    lichess_id: str
    avatar: Optional[HttpUrl]
    created_at: Optional[datetime]
    seen_at: Optional[datetime]
    ratings: dict[str, int] | None = None
    counts: dict[str, int] | None = None


class GamePublic(BaseModel):
    id: int
    game_id: str
    white: str
    black: str
    result: str
    opening: str
    time_class: str
    played_at: Optional[datetime] = None
    pgn: Optional[str] = None


class GamesResponse(BaseModel):
    games: list[GamePublic]
    total: int
    page: int
    per_page: int


class SyncRequest(BaseModel):
    force: bool = False
