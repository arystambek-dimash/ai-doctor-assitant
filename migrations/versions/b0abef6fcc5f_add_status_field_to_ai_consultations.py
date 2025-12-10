"""add status field to ai consultations

Revision ID: b0abef6fcc5f
Revises: 98359b615576
Create Date: 2025-12-09 21:24:44.484857

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0abef6fcc5f'
down_revision: Union[str, Sequence[str], None] = '98359b615576'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add status column to ai_consultations table
    op.add_column('ai_consultations',
                  sa.Column('status', sa.String(20), nullable=False, server_default='active'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove status column from ai_consultations table
    op.drop_column('ai_consultations', 'status')
