from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String(20), default="customer", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    customer = relationship(
        "Customer",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(15), unique=True, nullable=False)
    address = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user = relationship("User", back_populates="customer")
    vehicles = relationship(
        "Vehicle",
        back_populates="customer",
        cascade="all, delete-orphan"
    )


class Vehicle(Base):
    __tablename__ = "vehicles"

    vehicle_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(
        Integer,
        ForeignKey("customers.customer_id", ondelete="CASCADE"),
        nullable=False
    )

    registration_no = Column(String(20), unique=True, nullable=False)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    vehicle_type = Column(String(30), nullable=False)
    manufacturing_year = Column(Integer, nullable=True)
    color = Column(String(30), nullable=True)
    purchase_price = Column(Numeric(12, 2), nullable=True)

    customer = relationship("Customer", back_populates="vehicles")
    insurance_records = relationship(
        "Insurance",
        back_populates="vehicle",
        cascade="all, delete-orphan"
    )
    service_records = relationship(
        "ServiceRecord",
        back_populates="vehicle",
        cascade="all, delete-orphan"
    )


class Insurance(Base):
    __tablename__ = "insurance"

    insurance_id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(
        Integer,
        ForeignKey("vehicles.vehicle_id", ondelete="CASCADE"),
        nullable=False
    )

    policy_number = Column(String(50), unique=True, nullable=False)
    insurance_company = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    premium_amount = Column(Numeric(10, 2), nullable=True)
    status = Column(String(20), nullable=True)

    vehicle = relationship("Vehicle", back_populates="insurance_records")


class ServiceCenter(Base):
    __tablename__ = "service_centers"

    service_center_id = Column(Integer, primary_key=True, index=True)
    center_name = Column(String(100), nullable=False)
    phone = Column(String(15), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(50), nullable=True)
    rating = Column(Numeric(2, 1), nullable=True)

    service_records = relationship(
        "ServiceRecord",
        back_populates="service_center"
    )


class ServiceRecord(Base):
    __tablename__ = "service_records"

    service_id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(
        Integer,
        ForeignKey("vehicles.vehicle_id", ondelete="CASCADE"),
        nullable=False
    )
    service_center_id = Column(
        Integer,
        ForeignKey("service_centers.service_center_id", ondelete="CASCADE"),
        nullable=False
    )

    service_date = Column(Date, nullable=False)
    service_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    odometer_reading = Column(Integer, nullable=True)
    service_cost = Column(Numeric(10, 2), nullable=True)
    status = Column(String(20), nullable=True)

    vehicle = relationship("Vehicle", back_populates="service_records")
    service_center = relationship(
        "ServiceCenter",
        back_populates="service_records"
    )
    parts = relationship(
        "VehiclePart",
        back_populates="service_record",
        cascade="all, delete-orphan"
    )


class VehiclePart(Base):
    __tablename__ = "vehicle_parts"

    part_id = Column(Integer, primary_key=True, index=True)
    service_id = Column(
        Integer,
        ForeignKey("service_records.service_id", ondelete="CASCADE"),
        nullable=False
    )

    part_name = Column(String(100), nullable=False)
    part_number = Column(String(50), unique=True, nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=True)
    warranty_months = Column(Integer, nullable=True)

    service_record = relationship("ServiceRecord", back_populates="parts")
