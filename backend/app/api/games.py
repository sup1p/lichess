import logging
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_session
from app.models.models import User
from app.services import crud

logger = logging.getLogger(__name__)
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
    logger.info(f"Fetching games for user {user.username}: page={page}, per_page={per_page}, opening={opening}, result={result}, time_class={time_class}")
    result = await crud.list_games(
        session=session,
        user_id=user.id,
        page=page,
        per_page=per_page,
        opening=opening,
        result=result,
        time_class=time_class,
    )
    
    # Format response
    return {
        "games": [
            {
                "id": g.id,
                "game_id": g.game_id,
                "white": g.white,
                "black": g.black,
                "result": g.result,
                "opening": g.opening,
                "time_class": g.time_class,
                "played_at": g.played_at.isoformat() if g.played_at else None,
                "pgn": g.pgn,
            }
            for g in result["games"]
        ],
        "total": result["total"],
        "page": result["page"],
        "per_page": result["per_page"],
    }
