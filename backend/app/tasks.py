from datetime import datetime, timezone

from sqlalchemy import select

from app.services.celery_app import celery_app
from app.core.db import AsyncSessionLocal as async_session_maker
from app.services.lichess import get_games
from app.models.models import Game


@celery_app.task
def sync_recent_games():
    """Sync recent games from Lichess for all users."""
    import asyncio

    async def _sync():
        async with async_session_maker() as session:
            from app.models.models import User

            # Get all users
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            if not users:
                return {"error": "No users found"}

            total_synced = 0
            for user in users:
                games_data = await get_games(
                    user.username, user.access_token, max_games=50
                )
            
                games_count = 0
                for game in games_data:
                    game_id = game.get("id")
                    if not game_id:
                        continue

                    existing = await session.execute(
                        select(Game).where(
                            Game.user_id == user.id, Game.game_id == game_id
                        )
                    )
                    if existing.scalars().first():
                        continue

                    players = game.get("players", {})
                    white = players.get("white", {}).get("user", {}).get("name", "Unknown")
                    black = players.get("black", {}).get("user", {}).get("name", "Unknown")
                    
                    winner = game.get("winner")
                    if winner == "white":
                        result = "1-0"
                    elif winner == "black":
                        result = "0-1"
                    else:
                        result = "1/2-1/2"

                    opening = game.get("opening", {}).get("name", "Unknown")
                    speed = game.get("speed", "Unknown")
                    
                    played_at = None
                    if created_at := game.get("createdAt"):
                        played_at = datetime.fromtimestamp(created_at / 1000, tz=timezone.utc)

                    new_game = Game(
                        user_id=user.id,
                        game_id=game_id,
                        white=white,
                        black=black,
                        result=result,
                        opening=opening,
                        time_class=speed,
                        played_at=played_at,
                        pgn=game.get("pgn"),
                    )
                    session.add(new_game)
                    games_count += 1

                total_synced += games_count

            await session.commit()
            return {"users_synced": len(users), "games_synced": total_synced}

    return asyncio.run(_sync())
