import logging
from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.services.celery_app import celery_app
from app.core.config import get_settings
from app.models.models import Game, User

logger = logging.getLogger(__name__)
settings = get_settings()

# Create synchronous engine for Celery tasks
sync_engine = create_engine(
    settings.database_url.replace("+asyncpg", "").replace("postgresql+asyncpg", "postgresql"),
    pool_pre_ping=True,
)
SyncSessionLocal = sessionmaker(bind=sync_engine)


def _save_games_to_db(session, user, games_data) -> int:
    """Helper function to save games to database. Returns count of new games."""
    games_count = 0
    for game in games_data:
        game_id = game.get("id")
        if not game_id:
            continue

        existing = session.execute(
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
    
    return games_count


@celery_app.task
def sync_all_user_games(user_id: int):
    """Sync ALL games for a specific user (called on first login).
    
    Fetches games in batches of 50 until no more games are available.
    Uses 'until' parameter to paginate through history.
    """
    import asyncio
    from app.services.lichess import get_games
    
    with SyncSessionLocal() as session:
        result = session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        
        if not user:
            return {"error": "User not found"}
        
        total_synced = 0
        batch_size = 30
        until_timestamp = None  # Start from most recent
        
        while True:
            # Fetch batch of games
            games_data = asyncio.run(get_games(
                user.username, 
                user.access_token, 
                max_games=batch_size,
                until=until_timestamp
            ))
            
            if not games_data:
                break  # No more games
            
            logger.info(f"sync_all: Fetched {len(games_data)} games for user {user.username}, until={until_timestamp}")
            
            # Save games to database
            games_count = _save_games_to_db(session, user, games_data)
            total_synced += games_count
            
            # Commit after each batch for reliability
            session.commit()
            logger.info(f"sync_all: Saved {games_count} new games (total: {total_synced})")
            
            # If we got less than batch_size, we've reached the end
            if len(games_data) < batch_size:
                break
            
            # Get the oldest game's timestamp for next batch
            oldest_game = games_data[-1]
            if created_at := oldest_game.get("createdAt"):
                until_timestamp = created_at - 1  # -1ms to not include same game
            else:
                break  # Can't paginate without timestamp
        
        logger.info(f"sync_all: Completed for user {user.username}, total synced: {total_synced}")
        return {"user_id": user_id, "games_synced": total_synced}


@celery_app.task
def sync_recent_games():
    """Sync recent games (last 10) for all users.
    
    Called periodically by Celery Beat to keep games up to date.
    """
    import asyncio
    from app.services.lichess import get_games
    
    with SyncSessionLocal() as session:
        result = session.execute(select(User))
        users = result.scalars().all()
        
        if not users:
            return {"error": "No users found"}

        total_synced = 0
        for user in users:
            # Fetch only last 10 games for periodic sync
            games_data = asyncio.run(get_games(
                user.username, user.access_token, max_games=10
            ))
            
            games_count = _save_games_to_db(session, user, games_data)
            total_synced += games_count

        session.commit()
        return {"users_synced": len(users), "games_synced": total_synced}
