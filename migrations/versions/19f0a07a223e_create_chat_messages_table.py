"""create chat messages table

Revision ID: 19f0a07a223e
Revises: b0abef6fcc5f
Create Date: 2025-12-09 21:30:23.664146

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19f0a07a223e'
down_revision: Union[str, Sequence[str], None] = 'b0abef6fcc5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('consultation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['consultation_id'], ['ai_consultations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_messages_consultation_id'), 'chat_messages', ['consultation_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop chat_messages table
    op.drop_index(op.f('ix_chat_messages_consultation_id'), table_name='chat_messages')
    op.drop_table('chat_messages')
