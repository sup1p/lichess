from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.services.lichess import get_account
from app.models.models import User

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/")
async def get_profile(user: User = Depends(get_current_user)):
    """Get user profile from Lichess API."""
    profile = await get_account(user.access_token)
    return profile
