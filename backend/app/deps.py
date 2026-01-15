from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_session
from backend.app.models.models import User


async def get_db_session() -> AsyncSession:
    async for session in get_session():
        yield session


async def get_current_user(
    session: AsyncSession = Depends(get_db_session),
    x_user: str | None = None,
) -> User:
    if not x_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user context")
    result = await session.execute(select(User).where(User.username == x_user))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
