from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lichess_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    token_type: Mapped[str] = mapped_column(String(32), nullable=False, default="Bearer")
    scope: Mapped[Optional[str]] = mapped_column(Text)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    games: Mapped[list["Game"]] = relationship("Game", back_populates="user", cascade="all, delete-orphan")


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    game_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    white: Mapped[str] = mapped_column(String(64))
    black: Mapped[str] = mapped_column(String(64))
    result: Mapped[str] = mapped_column(String(16))
    opening: Mapped[str] = mapped_column(String(255))
    time_class: Mapped[str] = mapped_column(String(32))
    played_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True)
    pgn: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped[User] = relationship("User", back_populates="games")
