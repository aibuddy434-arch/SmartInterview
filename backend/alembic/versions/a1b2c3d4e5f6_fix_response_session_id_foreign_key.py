"""fix response session_id foreign key

Revision ID: a1b2c3d4e5f6
Revises: 8ea50fe6fc24
Create Date: 2024-12-14

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '7161ddf73ccd'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the old foreign key constraint on responses table
    op.drop_constraint('responses_ibfk_1', 'responses', type_='foreignkey')
    
    # Create new foreign key constraint pointing to session_id instead of id
    op.create_foreign_key(
        'responses_session_id_fkey',
        'responses',
        'interview_sessions',
        ['session_id'],
        ['session_id']
    )
    
    # Drop the old foreign key constraint on reports table
    op.drop_constraint('reports_ibfk_1', 'reports', type_='foreignkey')
    
    # Create new foreign key constraint pointing to session_id instead of id
    op.create_foreign_key(
        'reports_session_id_fkey',
        'reports',
        'interview_sessions',
        ['session_id'],
        ['session_id']
    )


def downgrade():
    # Revert: Drop new foreign key constraint on responses table
    op.drop_constraint('responses_session_id_fkey', 'responses', type_='foreignkey')
    
    # Recreate old foreign key constraint pointing to id
    op.create_foreign_key(
        'responses_ibfk_1',
        'responses',
        'interview_sessions',
        ['session_id'],
        ['id']
    )
    
    # Revert: Drop new foreign key constraint on reports table
    op.drop_constraint('reports_session_id_fkey', 'reports', type_='foreignkey')
    
    # Recreate old foreign key constraint pointing to id
    op.create_foreign_key(
        'reports_ibfk_1',
        'reports',
        'interview_sessions',
        ['session_id'],
        ['id']
    )
