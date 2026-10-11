from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="customer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "customers",
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=15), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("customer_id"),
        sa.UniqueConstraint("user_id"),
        sa.UniqueConstraint("phone")
    )
    op.create_index(op.f("ix_customers_customer_id"), "customers", ["customer_id"], unique=False)
    op.create_index(op.f("ix_customers_email"), "customers", ["email"], unique=True)

    op.create_table(
        "service_centers",
        sa.Column("service_center_id", sa.Integer(), nullable=False),
        sa.Column("center_name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=15), nullable=True),
        sa.Column("email", sa.String(length=100), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(length=50), nullable=True),
        sa.Column("rating", sa.Numeric(precision=2, scale=1), nullable=True),
        sa.PrimaryKeyConstraint("service_center_id")
    )
    op.create_index(op.f("ix_service_centers_service_center_id"), "service_centers", ["service_center_id"], unique=False)

    op.create_table(
        "vehicles",
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("registration_no", sa.String(length=20), nullable=False),
        sa.Column("brand", sa.String(length=50), nullable=False),
        sa.Column("model", sa.String(length=50), nullable=False),
        sa.Column("vehicle_type", sa.String(length=30), nullable=False),
        sa.Column("manufacturing_year", sa.Integer(), nullable=True),
        sa.Column("color", sa.String(length=30), nullable=True),
        sa.Column("purchase_price", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.customer_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("vehicle_id"),
        sa.UniqueConstraint("registration_no")
    )
    op.create_index(op.f("ix_vehicles_vehicle_id"), "vehicles", ["vehicle_id"], unique=False)

    op.create_table(
        "insurance",
        sa.Column("insurance_id", sa.Integer(), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("policy_number", sa.String(length=50), nullable=False),
        sa.Column("insurance_company", sa.String(length=100), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("premium_amount", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.vehicle_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("insurance_id"),
        sa.UniqueConstraint("policy_number")
    )
    op.create_index(op.f("ix_insurance_insurance_id"), "insurance", ["insurance_id"], unique=False)

    op.create_table(
        "service_records",
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("service_center_id", sa.Integer(), nullable=False),
        sa.Column("service_date", sa.Date(), nullable=False),
        sa.Column("service_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("odometer_reading", sa.Integer(), nullable=True),
        sa.Column("service_cost", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(["service_center_id"], ["service_centers.service_center_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.vehicle_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("service_id")
    )
    op.create_index(op.f("ix_service_records_service_id"), "service_records", ["service_id"], unique=False)

    op.create_table(
        "vehicle_parts",
        sa.Column("part_id", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("part_name", sa.String(length=100), nullable=False),
        sa.Column("part_number", sa.String(length=50), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("total_price", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("warranty_months", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["service_id"], ["service_records.service_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("part_id"),
        sa.UniqueConstraint("part_number")
    )
    op.create_index(op.f("ix_vehicle_parts_part_id"), "vehicle_parts", ["part_id"], unique=False)


def downgrade() -> None:
    op.drop_table("vehicle_parts")
    op.drop_table("service_records")
    op.drop_table("insurance")
    op.drop_table("vehicles")
    op.drop_table("service_centers")
    op.drop_table("customers")
    op.drop_table("users")
