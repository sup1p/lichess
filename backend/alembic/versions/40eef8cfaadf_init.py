"""init

Revision ID: 40eef8cfaadf
Revises: 
Create Date: 2026-01-14 17:11:32.903313

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40eef8cfaadf'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lichess_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("username", sa.String(length=64), nullable=False, unique=True),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("token_type", sa.String(length=32), nullable=False),
        sa.Column("scope", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "games",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("game_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("white", sa.String(length=64), nullable=False),
        sa.Column("black", sa.String(length=64), nullable=False),
        sa.Column("result", sa.String(length=16), nullable=False),
        sa.Column("opening", sa.String(length=255), nullable=False),
        sa.Column("time_class", sa.String(length=32), nullable=False),
        sa.Column("played_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pgn", sa.Text(), nullable=True),
    )

    op.create_index("ix_games_user_id", "games", ["user_id"])
    op.create_index("ix_games_game_id", "games", ["game_id"])
    op.create_index("ix_games_played_at", "games", ["played_at"])


def downgrade() -> None:
    op.drop_index("ix_games_played_at", table_name="games")
    op.drop_index("ix_games_game_id", table_name="games")
    op.drop_index("ix_games_user_id", table_name="games")
    op.drop_table("games")
    op.drop_table("users")
