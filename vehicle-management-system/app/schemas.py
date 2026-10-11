from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class ORMBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(default="customer", pattern="^(customer|admin)$")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(ORMBaseSchema):
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class CustomerCreate(BaseModel):
    user_id: int | None = None
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=15)
    address: str | None = None


class CustomerUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=7, max_length=15)
    address: str | None = None


class CustomerResponse(ORMBaseSchema):
    customer_id: int
    user_id: int
    full_name: str
    email: EmailStr
    phone: str
    address: str | None
    created_at: datetime
    updated_at: datetime


class VehicleCreate(BaseModel):
    customer_id: int | None = None
    registration_no: str = Field(min_length=1, max_length=20)
    brand: str = Field(min_length=1, max_length=50)
    model: str = Field(min_length=1, max_length=50)
    vehicle_type: str = Field(min_length=1, max_length=30)
    manufacturing_year: int | None = Field(default=None, ge=1886, le=2100)
    color: str | None = Field(default=None, max_length=30)
    purchase_price: Decimal | None = Field(default=None, ge=0)


class VehicleUpdate(BaseModel):
    customer_id: int | None = None
    registration_no: str | None = Field(default=None, min_length=1, max_length=20)
    brand: str | None = Field(default=None, min_length=1, max_length=50)
    model: str | None = Field(default=None, min_length=1, max_length=50)
    vehicle_type: str | None = Field(default=None, min_length=1, max_length=30)
    manufacturing_year: int | None = Field(default=None, ge=1886, le=2100)
    color: str | None = Field(default=None, max_length=30)
    purchase_price: Decimal | None = Field(default=None, ge=0)


class VehicleResponse(ORMBaseSchema):
    vehicle_id: int
    customer_id: int
    registration_no: str
    brand: str
    model: str
    vehicle_type: str
    manufacturing_year: int | None
    color: str | None
    purchase_price: Decimal | None


class InsuranceCreate(BaseModel):
    vehicle_id: int
    policy_number: str = Field(min_length=1, max_length=50)
    insurance_company: str = Field(min_length=1, max_length=100)
    start_date: date
    end_date: date
    premium_amount: Decimal | None = Field(default=None, ge=0)
    status: str | None = Field(default=None, max_length=20)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class InsuranceUpdate(BaseModel):
    vehicle_id: int | None = None
    policy_number: str | None = Field(default=None, min_length=1, max_length=50)
    insurance_company: str | None = Field(default=None, min_length=1, max_length=100)
    start_date: date | None = None
    end_date: date | None = None
    premium_amount: Decimal | None = Field(default=None, ge=0)
    status: str | None = Field(default=None, max_length=20)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date is not None and self.end_date is not None:
            if self.end_date < self.start_date:
                raise ValueError("end_date must be on or after start_date")
        return self


class InsuranceResponse(ORMBaseSchema):
    insurance_id: int
    vehicle_id: int
    policy_number: str
    insurance_company: str
    start_date: date
    end_date: date
    premium_amount: Decimal | None
    status: str | None


class ServiceCenterCreate(BaseModel):
    center_name: str = Field(min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=15)
    email: EmailStr | None = None
    address: str | None = None
    city: str | None = Field(default=None, max_length=50)
    rating: Decimal | None = Field(default=None, ge=0, le=5)


class ServiceCenterUpdate(BaseModel):
    center_name: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=15)
    email: EmailStr | None = None
    address: str | None = None
    city: str | None = Field(default=None, max_length=50)
    rating: Decimal | None = Field(default=None, ge=0, le=5)


class ServiceCenterResponse(ORMBaseSchema):
    service_center_id: int
    center_name: str
    phone: str | None
    email: str | None
    address: str | None
    city: str | None
    rating: Decimal | None


class ServiceRecordCreate(BaseModel):
    vehicle_id: int
    service_center_id: int
    service_date: date
    service_type: str = Field(min_length=1, max_length=50)
    description: str | None = None
    odometer_reading: int | None = Field(default=None, ge=0)
    service_cost: Decimal | None = Field(default=None, ge=0)
    status: str | None = Field(default=None, max_length=20)


class ServiceRecordUpdate(BaseModel):
    vehicle_id: int | None = None
    service_center_id: int | None = None
    service_date: date | None = None
    service_type: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = None
    odometer_reading: int | None = Field(default=None, ge=0)
    service_cost: Decimal | None = Field(default=None, ge=0)
    status: str | None = Field(default=None, max_length=20)


class ServiceRecordResponse(ORMBaseSchema):
    service_id: int
    vehicle_id: int
    service_center_id: int
    service_date: date
    service_type: str
    description: str | None
    odometer_reading: int | None
    service_cost: Decimal | None
    status: str | None


class VehiclePartCreate(BaseModel):
    service_id: int
    part_name: str = Field(min_length=1, max_length=100)
    part_number: str | None = Field(default=None, max_length=50)
    quantity: int = Field(ge=1)
    unit_price: Decimal = Field(ge=0)
    warranty_months: int | None = Field(default=None, ge=0)


class VehiclePartUpdate(BaseModel):
    service_id: int | None = None
    part_name: str | None = Field(default=None, min_length=1, max_length=100)
    part_number: str | None = Field(default=None, max_length=50)
    quantity: int | None = Field(default=None, ge=1)
    unit_price: Decimal | None = Field(default=None, ge=0)
    warranty_months: int | None = Field(default=None, ge=0)


class VehiclePartResponse(ORMBaseSchema):
    part_id: int
    service_id: int
    part_name: str
    part_number: str | None
    quantity: int
    unit_price: Decimal
    total_price: Decimal | None
    warranty_months: int | None


class VehicleCountByType(BaseModel):
    vehicle_type: str
    total_vehicles: int


class ServiceCostSummary(BaseModel):
    total_services: int
    total_service_cost: Decimal
    average_service_cost: Decimal


class CustomerVehicleSummary(BaseModel):
    customer_id: int
    customer_name: str
    total_vehicles: int


class VehicleServiceHistory(BaseModel):
    service_id: int
    service_date: date
    service_type: str
    service_cost: Decimal | None
    service_center: str


class PartsCostSummary(BaseModel):
    total_parts: int
    total_quantity: int
    total_parts_cost: Decimal


class InsuranceStatusSummary(BaseModel):
    status: str | None
    total_policies: int
