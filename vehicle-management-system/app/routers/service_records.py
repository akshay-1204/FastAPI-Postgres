from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_active_user
from app.models import Customer, ServiceCenter, ServiceRecord, User, Vehicle
from app.schemas import (
    ServiceRecordCreate,
    ServiceRecordResponse,
    ServiceRecordUpdate,
)

router = APIRouter(
    prefix="/service-records",
    tags=["Service Records"]
)


@router.post(
    "/",
    response_model=ServiceRecordResponse,
    status_code=status.HTTP_201_CREATED
)
def create_service_record(
    record_data: ServiceRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    vehicle = db.query(Vehicle).filter(
        Vehicle.vehicle_id == record_data.vehicle_id
    ).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    if current_user.role != "admin" and vehicle.customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to create service records for this vehicle"
        )

    center = db.query(ServiceCenter).filter(
        ServiceCenter.service_center_id == record_data.service_center_id
    ).first()

    if not center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service center not found"
        )

    new_record = ServiceRecord(
        vehicle_id=record_data.vehicle_id,
        service_center_id=record_data.service_center_id,
        service_date=record_data.service_date,
        service_type=record_data.service_type,
        description=record_data.description,
        odometer_reading=record_data.odometer_reading,
        service_cost=record_data.service_cost,
        status=record_data.status
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return new_record


@router.get("/", response_model=list[ServiceRecordResponse])
def get_service_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    if current_user.role == "admin":
        return db.query(ServiceRecord).all()

    return (
        db.query(ServiceRecord)
        .join(Vehicle, ServiceRecord.vehicle_id == Vehicle.vehicle_id)
        .join(Customer, Vehicle.customer_id == Customer.customer_id)
        .filter(Customer.user_id == current_user.id)
        .all()
    )


@router.get("/{service_id}", response_model=ServiceRecordResponse)
def get_service_record(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    record = db.query(ServiceRecord).filter(
        ServiceRecord.service_id == service_id
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service record not found"
        )

    if current_user.role != "admin" and record.vehicle.customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this service record"
        )

    return record


@router.put("/{service_id}", response_model=ServiceRecordResponse)
def update_service_record(
    service_id: int,
    record_data: ServiceRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    record = db.query(ServiceRecord).filter(
        ServiceRecord.service_id == service_id
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service record not found"
        )

    if current_user.role != "admin" and record.vehicle.customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to modify this service record"
        )

    update_data = record_data.model_dump(exclude_unset=True)

    if "vehicle_id" in update_data and update_data["vehicle_id"] is not None:
        target_vehicle = db.query(Vehicle).filter(
            Vehicle.vehicle_id == update_data["vehicle_id"]
        ).first()

        if not target_vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )

        if current_user.role != "admin" and target_vehicle.customer.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot transfer service record to vehicle owned by another user"
            )

    if "service_center_id" in update_data and update_data["service_center_id"] is not None:
        target_center = db.query(ServiceCenter).filter(
            ServiceCenter.service_center_id == update_data["service_center_id"]
        ).first()

        if not target_center:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service center not found"
            )

    for field, value in update_data.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)

    return record


@router.delete("/{service_id}")
def delete_service_record(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    record = db.query(ServiceRecord).filter(
        ServiceRecord.service_id == service_id
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service record not found"
        )

    if current_user.role != "admin" and record.vehicle.customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to delete this service record"
        )

    db.delete(record)
    db.commit()

    return {"message": "Service record deleted successfully"}
