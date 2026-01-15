from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_session
from app.models.models import Game, User

router = APIRouter(prefix="/games", tags=["games"])


@router.get("/")
async def list_games(
    page: int = 1,
    per_page: int = 20,
    opening: Optional[str] = None,
    result: Optional[str] = None,
    time_class: Optional[str] = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """List games with pagination and filtering."""
    filters = [Game.user_id == user.id]
    if opening:
        filters.append(Game.opening.ilike(f"%{opening}%"))
    if result:
        filters.append(Game.result == result)
    if time_class:
        filters.append(Game.time_class == time_class)

    query = select(Game).where(and_(*filters)).order_by(Game.played_at.desc())
    query = query.limit(per_page).offset((page - 1) * per_page)

    result_query = await session.execute(query)
    games = result_query.scalars().all()

    count_query = select(func.count()).select_from(Game).where(and_(*filters))
    count_result = await session.execute(count_query)
    total = count_result.scalar() or 0

    return {
        "games": [
            {
                "id": g.id,
                "lichess_id": g.lichess_id,
                "white": g.white,
                "black": g.black,
                "result": g.result,
                "opening": g.opening,
                "time_class": g.time_class,
                "played_at": g.played_at.isoformat() if g.played_at else None,
                "pgn": g.pgn,
            }
            for g in games
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }
