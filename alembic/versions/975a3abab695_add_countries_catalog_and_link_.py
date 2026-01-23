"""add countries catalog and link organizations

Revision ID: 975a3abab695
Revises: b2948a4f42f0
Create Date: 2026-01-22 18:28:39.855260

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '975a3abab695'
down_revision: Union[str, Sequence[str], None] = 'b2948a4f42f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # ==========================
    # CREATE COUNTRIES TABLE
    # ==========================
    if not inspector.has_table('countries'):
        op.create_table(
            'countries',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('code', sa.String(length=5), nullable=False, unique=True),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('phone_code', sa.String(length=10), nullable=False),
            sa.Column('is_active', sa.Boolean(), server_default=sa.true(), nullable=False),
        )

        op.execute("""
            INSERT INTO countries (code, name, phone_code) VALUES
            ('EC', 'Ecuador', '+593'),
            ('CO', 'Colombia', '+57'),
            ('PE', 'Perú', '+51'),
            ('MX', 'México', '+52'),
            ('AR', 'Argentina', '+54'),
            ('US', 'Estados Unidos', '+1')
        """)

    # ==========================
    # ADD country_id TO organizations
    # ==========================
    columns = [col['name'] for col in inspector.get_columns('organizations')]

    if 'country_id' not in columns:
        op.add_column(
            'organizations',
            sa.Column('country_id', sa.Integer(), nullable=True)
        )

        op.execute("""
            UPDATE organizations
            SET country_id = (
                SELECT id FROM countries WHERE code = 'EC'
            )
        """)

        op.alter_column('organizations', 'country_id', nullable=False)

        op.create_foreign_key(
            'fk_organizations_country',
            'organizations',
            'countries',
            ['country_id'],
            ['id']
        )

    # ==========================
    # REMOVE code_telephone (safe)
    # ==========================
    if 'code_telephone' in columns:
        with op.batch_alter_table('organizations') as batch_op:
            batch_op.drop_column('code_telephone')


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    columns = [col['name'] for col in inspector.get_columns('organizations')]

    if 'code_telephone' not in columns:
        op.add_column(
            'organizations',
            sa.Column('code_telephone', sa.String(length=10))
        )

    op.drop_constraint('fk_organizations_country', 'organizations', type_='foreignkey')
    op.drop_column('organizations', 'country_id')
    op.drop_table('countries')
