"""make ai consultation fields nullable

Revision ID: 98359b615576
Revises: e41989e9ee62
Create Date: 2025-12-09 21:22:55.377647

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '98359b615576'
down_revision: Union[str, Sequence[str], None] = 'e41989e9ee62'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Make ai_consultations fields nullable
    op.alter_column('ai_consultations', 'recommended_specialization',
                    existing_type=sa.String(100),
                    nullable=True)
    op.alter_column('ai_consultations', 'confidence',
                    existing_type=sa.Float(),
                    nullable=True)
    op.alter_column('ai_consultations', 'ai_response_raw',
                    existing_type=sa.Text(),
                    nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Make ai_consultations fields NOT nullable again
    op.alter_column('ai_consultations', 'ai_response_raw',
                    existing_type=sa.Text(),
                    nullable=False)
    op.alter_column('ai_consultations', 'confidence',
                    existing_type=sa.Float(),
                    nullable=False)
    op.alter_column('ai_consultations', 'recommended_specialization',
                    existing_type=sa.String(100),
                    nullable=False)
