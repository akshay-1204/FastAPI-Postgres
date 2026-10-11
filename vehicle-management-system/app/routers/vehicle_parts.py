from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_active_user
from app.models import Customer, ServiceRecord, User, Vehicle, VehiclePart
from app.schemas import (
    VehiclePartCreate,
    VehiclePartResponse,
    VehiclePartUpdate,
)

router = APIRouter(
    prefix="/vehicle-parts",
    tags=["Vehicle Parts"]
)


@router.post(
    "/",
    response_model=VehiclePartResponse,
    status_code=status.HTTP_201_CREATED
)
def create_vehicle_part(
    part_data: VehiclePartCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    service_record = db.query(ServiceRecord).filter(
        ServiceRecord.service_id == part_data.service_id
    ).first()

    if not service_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service record not found"
        )

    if current_user.role != "admin" and service_record.vehicle.customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to add parts to this service record"
        )

    if part_data.part_number is not None:
        existing_part = db.query(VehiclePart).filter(
            VehiclePart.part_number == part_data.part_number
        ).first()

        if existing_part:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Part number already exists"
            )

    total_price = Decimal(str(part_data.quantity)) * part_data.unit_price

    new_part = VehiclePart(
        service_id=part_data.service_id,
        part_name=part_data.part_name,
        part_number=part_data.part_number,
        quantity=part_data.quantity,
        unit_price=part_data.unit_price,
        total_price=total_price,
        warranty_months=part_data.warranty_months
    )

    db.add(new_part)
    db.commit()
    db.refresh(new_part)

    return new_part


@router.get("/", response_model=list[VehiclePartResponse])
def get_vehicle_parts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    if current_user.role == "admin":
        return db.query(VehiclePart).all()

    return (
        db.query(VehiclePart)
        .join(ServiceRecord, VehiclePart.service_id == ServiceRecord.service_id)
        .join(Vehicle, ServiceRecord.vehicle_id == Vehicle.vehicle_id)
        .join(Customer, Vehicle.customer_id == Customer.customer_id)
        .filter(Customer.user_id == current_user.id)
        .all()
    )


@router.get("/{part_id}", response_model=VehiclePartResponse)
def get_vehicle_part(
    part_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    part = db.query(VehiclePart).filter(
        VehiclePart.part_id == part_id
    ).first()

    if not part:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle part not found"
        )

    if current_user.role != "admin" and part.service_record.vehicle.customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this vehicle part"
        )

    return part


@router.put("/{part_id}", response_model=VehiclePartResponse)
def update_vehicle_part(
    part_id: int,
    part_data: VehiclePartUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    part = db.query(VehiclePart).filter(
        VehiclePart.part_id == part_id
    ).first()

    if not part:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle part not found"
        )

    if current_user.role != "admin" and part.service_record.vehicle.customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to modify this vehicle part"
        )

    update_data = part_data.model_dump(exclude_unset=True)

    if "service_id" in update_data and update_data["service_id"] is not None:
        target_record = db.query(ServiceRecord).filter(
            ServiceRecord.service_id == update_data["service_id"]
        ).first()

        if not target_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service record not found"
            )

        if current_user.role != "admin" and target_record.vehicle.customer.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot transfer part to service record owned by another user"
            )

    if "part_number" in update_data and update_data["part_number"] is not None:
        existing_part = db.query(VehiclePart).filter(
            VehiclePart.part_number == update_data["part_number"],
            VehiclePart.part_id != part_id
        ).first()

        if existing_part:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Part number already exists"
            )

    for field, value in update_data.items():
        setattr(part, field, value)

    if "quantity" in update_data or "unit_price" in update_data:
        quantity = update_data.get("quantity", part.quantity)
        unit_price = update_data.get("unit_price", part.unit_price)
        part.total_price = Decimal(str(quantity)) * unit_price

    db.commit()
    db.refresh(part)

    return part


@router.delete("/{part_id}")
def delete_vehicle_part(
    part_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    part = db.query(VehiclePart).filter(
        VehiclePart.part_id == part_id
    ).first()

    if not part:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle part not found"
        )

    if current_user.role != "admin" and part.service_record.vehicle.customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to delete this vehicle part"
        )

    db.delete(part)
    db.commit()

    return {"message": "Vehicle part deleted successfully"}
