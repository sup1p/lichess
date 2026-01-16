"""CRUD operations for database models."""
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Game, User
from app.schemas.schemas import TokenPayload


logger = logging.getLogger(__name__)


# User CRUD operations

async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID."""
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_user_by_lichess_id(session: AsyncSession, lichess_id: str) -> Optional[User]:
    """Get user by Lichess ID."""
    result = await session.execute(select(User).where(User.lichess_id == lichess_id))
    return result.scalars().first()


async def create_user(
    session: AsyncSession,
    lichess_id: str,
    username: str,
    token: TokenPayload,
) -> User:
    """Create new user."""
    logger.info(f"Creating new user: {username} (lichess_id={lichess_id})")
    expires_at = None
    if token.expires_in:
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=token.expires_in)
    
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
    await session.flush()
    return user


async def update_user_tokens(
    session: AsyncSession,
    user: User,
    username: str,
    token: TokenPayload,
) -> User:
    """Update user tokens."""
    expires_at = None
    if token.expires_in:
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=token.expires_in)
    
    user.username = username
    user.access_token = token.access_token
    user.refresh_token = token.refresh_token
    user.token_type = token.token_type
    user.scope = token.scope
    user.expires_at = expires_at
    user.updated_at = datetime.now(timezone.utc)
    await session.flush()
    return user


# Game CRUD operations

async def list_games(
    session: AsyncSession,
    user_id: int,
    page: int = 1,
    per_page: int = 20,
    opening: Optional[str] = None,
    result: Optional[str] = None,
    time_class: Optional[str] = None,
) -> Dict:
    """List games with pagination and filtering."""
    filters = [Game.user_id == user_id]
    
    if opening:
        filters.append(Game.opening.ilike(f"%{opening}%"))
    if result:
        filters.append(Game.result == result)
    if time_class:
        filters.append(Game.time_class == time_class)

    # Get games
    query = select(Game).where(and_(*filters)).order_by(Game.played_at.desc())
    query = query.limit(per_page).offset((page - 1) * per_page)
    result_query = await session.execute(query)
    games = result_query.scalars().all()

    # Get total count
    count_query = select(func.count()).select_from(Game).where(and_(*filters))
    count_result = await session.execute(count_query)
    total = count_result.scalar() or 0

    logger.info(f"Retrieved {len(games)} games for user_id={user_id} (total={total}, page={page})")
    return {
        "games": games,
        "total": total,
        "page": page,
        "per_page": per_page,
    }


async def get_game_stats(session: AsyncSession, user_id: int) -> Dict:
    """Get game statistics for user."""
    # Total games
    total_query = select(func.count()).select_from(Game).where(Game.user_id == user_id)
    total_result = await session.execute(total_query)
    total_games = total_result.scalar() or 0
    
    # Wins, losses, draws
    wins_query = select(func.count()).select_from(Game).where(
        Game.user_id == user_id, Game.result == "1-0"
    )
    wins_result = await session.execute(wins_query)
    wins = wins_result.scalar() or 0
    
    losses_query = select(func.count()).select_from(Game).where(
        Game.user_id == user_id, Game.result == "0-1"
    )
    losses_result = await session.execute(losses_query)
    losses = losses_result.scalar() or 0
    
    draws_query = select(func.count()).select_from(Game).where(
        Game.user_id == user_id, Game.result == "1/2-1/2"
    )
    draws_result = await session.execute(draws_query)
    draws = draws_result.scalar() or 0
    
    return {
        "total": total_games,
        "wins": wins,
        "losses": losses,
        "draws": draws,
    }

