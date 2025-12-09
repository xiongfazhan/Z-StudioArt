"""Add composite indexes for payment_orders

Revision ID: 004_add_composite_indexes
Revises: 003_add_updated_at_triggers
Create Date: 2025-12-09

Requirements: 11.3 - 添加复合索引优化查询性能
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_add_composite_indexes'
down_revision: Union[str, None] = '003_add_updated_at_triggers'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema.
    
    添加 payment_orders 表的复合索引：
    - ix_payment_orders_user_status: (user_id, status)
    - ix_payment_orders_user_created: (user_id, created_at)
    """
    conn = op.get_bind()
    
    # 添加 (user_id, status) 复合索引
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_payment_orders_user_status "
        "ON payment_orders (user_id, status)"
    ))
    
    # 添加 (user_id, created_at) 复合索引
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_payment_orders_user_created "
        "ON payment_orders (user_id, created_at)"
    ))


def downgrade() -> None:
    """Downgrade database schema.
    
    删除复合索引
    """
    op.drop_index('ix_payment_orders_user_status', table_name='payment_orders')
    op.drop_index('ix_payment_orders_user_created', table_name='payment_orders')
