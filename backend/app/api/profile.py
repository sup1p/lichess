from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.services.lichess import get_account
from app.models.models import User

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/")
async def get_profile(user: User = Depends(get_current_user)):
    """Get user profile from Lichess API."""
    profile = await get_account(user.access_token)
    
    # Extract ratings from perfs
    ratings = {}
    perfs = profile.get("perfs", {})
    for mode, data in perfs.items():
        if isinstance(data, dict) and "rating" in data:
            ratings[mode] = data["rating"]
    
    # Extract counts
    counts = profile.get("count", {})
    
    return {
        "username": profile.get("username"),
        "created_at": profile.get("createdAt"),
        "seen_at": profile.get("seenAt"),
        "ratings": ratings,
        "counts": counts,
    }
