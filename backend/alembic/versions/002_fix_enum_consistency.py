"""Fix database enum value consistency

Revision ID: 002_fix_enum_consistency
Revises: 001_add_auth_models
Create Date: 2025-12-09

Requirements: 11.1 - 修复 membershiptier 枚举值与 schemas.py 一致
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_fix_enum_consistency'
down_revision: Union[str, None] = '001_add_auth_models'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema.
    
    修复 membershiptier 枚举值：
    - 将 'FREE' 改为 'free'
    - 将 'BASIC' 改为 'basic'  
    - 将 'PRO' 改为 'professional'
    """
    conn = op.get_bind()
    
    # Step 1: 创建新的枚举类型
    conn.execute(sa.text(
        "DO $$ BEGIN "
        "CREATE TYPE membershiptier_new AS ENUM ('free', 'basic', 'professional'); "
        "EXCEPTION WHEN duplicate_object THEN null; "
        "END $$;"
    ))
    
    # Step 2: 更新 users 表中的 membership_tier 列
    # 先将列改为 VARCHAR 以便转换
    conn.execute(sa.text(
        "ALTER TABLE users ALTER COLUMN membership_tier DROP DEFAULT"
    ))
    conn.execute(sa.text(
        "ALTER TABLE users ALTER COLUMN membership_tier TYPE VARCHAR(20)"
    ))
    
    # Step 3: 更新现有数据的值
    conn.execute(sa.text(
        "UPDATE users SET membership_tier = 'free' WHERE membership_tier = 'FREE'"
    ))
    conn.execute(sa.text(
        "UPDATE users SET membership_tier = 'basic' WHERE membership_tier = 'BASIC'"
    ))
    conn.execute(sa.text(
        "UPDATE users SET membership_tier = 'professional' WHERE membership_tier = 'PRO'"
    ))
    
    # Step 4: 将列改为新的枚举类型
    conn.execute(sa.text(
        "ALTER TABLE users ALTER COLUMN membership_tier TYPE membershiptier_new "
        "USING membership_tier::membershiptier_new"
    ))
    
    # Step 5: 设置默认值
    conn.execute(sa.text(
        "ALTER TABLE users ALTER COLUMN membership_tier SET DEFAULT 'free'"
    ))
    
    # Step 6: 删除旧的枚举类型并重命名新的
    conn.execute(sa.text("DROP TYPE IF EXISTS membershiptier"))
    conn.execute(sa.text("ALTER TYPE membershiptier_new RENAME TO membershiptier"))


def downgrade() -> None:
    """Downgrade database schema.
    
    恢复 membershiptier 枚举值为原始大写格式
    """
    conn = op.get_bind()
    
    # Step 1: 创建旧的枚举类型
    conn.execute(sa.text(
        "CREATE TYPE membershiptier_old AS ENUM ('FREE', 'BASIC', 'PRO')"
    ))
    
    # Step 2: 将列改为 VARCHAR
    conn.execute(sa.text(
        "ALTER TABLE users ALTER COLUMN membership_tier TYPE VARCHAR(20)"
    ))
    
    # Step 3: 更新数据值
    conn.execute(sa.text(
        "UPDATE users SET membership_tier = 'FREE' WHERE membership_tier = 'free'"
    ))
    conn.execute(sa.text(
        "UPDATE users SET membership_tier = 'BASIC' WHERE membership_tier = 'basic'"
    ))
    conn.execute(sa.text(
        "UPDATE users SET membership_tier = 'PRO' WHERE membership_tier = 'professional'"
    ))
    
    # Step 4: 将列改为旧的枚举类型
    conn.execute(sa.text(
        "ALTER TABLE users ALTER COLUMN membership_tier TYPE membershiptier_old "
        "USING membership_tier::membershiptier_old"
    ))
    
    # Step 5: 设置默认值
    conn.execute(sa.text(
        "ALTER TABLE users ALTER COLUMN membership_tier SET DEFAULT 'FREE'"
    ))
    
    # Step 6: 删除新的枚举类型并重命名旧的
    conn.execute(sa.text("DROP TYPE IF EXISTS membershiptier"))
    conn.execute(sa.text("ALTER TYPE membershiptier_old RENAME TO membershiptier"))
