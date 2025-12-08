"""Add password_updated_at to users table

Revision ID: 001
Revises: 
Create Date: 2025-12-07 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add password_updated_at column to users table."""
    # Add the column as nullable
    op.add_column('users', 
        sa.Column('password_updated_at', sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    """Remove password_updated_at column from users table."""
    op.drop_column('users', 'password_updated_at')
