from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_active_user
from app.models import Customer, User, Vehicle
from app.schemas import VehicleCreate, VehicleResponse, VehicleUpdate

router = APIRouter(
    prefix="/vehicles",
    tags=["Vehicles"]
)


@router.post(
    "/",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED
)
def create_vehicle(
    vehicle_data: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    if current_user.role == "admin" and vehicle_data.customer_id is not None:
        customer = db.query(Customer).filter(
            Customer.customer_id == vehicle_data.customer_id
        ).first()
    else:
        customer = db.query(Customer).filter(
            Customer.user_id == current_user.id
        ).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer record required before creating vehicles"
        )

    existing_vehicle = db.query(Vehicle).filter(
        Vehicle.registration_no == vehicle_data.registration_no
    ).first()

    if existing_vehicle:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vehicle registration number already exists"
        )

    new_vehicle = Vehicle(
        customer_id=customer.customer_id,
        registration_no=vehicle_data.registration_no,
        brand=vehicle_data.brand,
        model=vehicle_data.model,
        vehicle_type=vehicle_data.vehicle_type,
        manufacturing_year=vehicle_data.manufacturing_year,
        color=vehicle_data.color,
        purchase_price=vehicle_data.purchase_price
    )

    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)

    return new_vehicle


@router.get("/", response_model=list[VehicleResponse])
def get_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    if current_user.role == "admin":
        return db.query(Vehicle).all()

    customer = db.query(Customer).filter(
        Customer.user_id == current_user.id
    ).first()

    if not customer:
        return []

    return db.query(Vehicle).filter(
        Vehicle.customer_id == customer.customer_id
    ).all()


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    vehicle = db.query(Vehicle).filter(
        Vehicle.vehicle_id == vehicle_id
    ).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    if current_user.role != "admin" and vehicle.customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this vehicle record"
        )

    return vehicle


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    vehicle = db.query(Vehicle).filter(
        Vehicle.vehicle_id == vehicle_id
    ).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    if current_user.role != "admin" and vehicle.customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to modify this vehicle record"
        )

    update_data = vehicle_data.model_dump(exclude_unset=True)

    if "customer_id" in update_data and update_data["customer_id"] is not None:
        target_customer = db.query(Customer).filter(
            Customer.customer_id == update_data["customer_id"]
        ).first()

        if not target_customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target customer not found"
            )

        if current_user.role != "admin" and target_customer.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot transfer vehicle to another customer"
            )

    if "registration_no" in update_data and update_data["registration_no"] is not None:
        existing_vehicle = db.query(Vehicle).filter(
            Vehicle.registration_no == update_data["registration_no"],
            Vehicle.vehicle_id != vehicle_id
        ).first()

        if existing_vehicle:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vehicle registration number already exists"
            )

    for field, value in update_data.items():
        setattr(vehicle, field, value)

    db.commit()
    db.refresh(vehicle)

    return vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_200_OK)
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    vehicle = db.query(Vehicle).filter(
        Vehicle.vehicle_id == vehicle_id
    ).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    if current_user.role != "admin" and vehicle.customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to delete this vehicle record"
        )

    db.delete(vehicle)
    db.commit()

    return {"message": "Vehicle deleted successfully"}
