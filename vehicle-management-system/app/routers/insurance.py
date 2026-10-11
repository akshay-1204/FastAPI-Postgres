from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_active_user
from app.models import Customer, Insurance, User, Vehicle
from app.schemas import InsuranceCreate, InsuranceResponse, InsuranceUpdate

router = APIRouter(
    prefix="/insurance",
    tags=["Insurance"]
)


@router.post(
    "/",
    response_model=InsuranceResponse,
    status_code=status.HTTP_201_CREATED
)
def create_insurance(
    insurance_data: InsuranceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    vehicle = db.query(Vehicle).filter(
        Vehicle.vehicle_id == insurance_data.vehicle_id
    ).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    if current_user.role != "admin" and vehicle.customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to create insurance for this vehicle"
        )

    existing_policy = db.query(Insurance).filter(
        Insurance.policy_number == insurance_data.policy_number
    ).first()

    if existing_policy:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Policy number already exists"
        )

    new_insurance = Insurance(
        vehicle_id=insurance_data.vehicle_id,
        policy_number=insurance_data.policy_number,
        insurance_company=insurance_data.insurance_company,
        start_date=insurance_data.start_date,
        end_date=insurance_data.end_date,
        premium_amount=insurance_data.premium_amount,
        status=insurance_data.status
    )

    db.add(new_insurance)
    db.commit()
    db.refresh(new_insurance)

    return new_insurance


@router.get("/", response_model=list[InsuranceResponse])
def get_all_insurance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    if current_user.role == "admin":
        return db.query(Insurance).all()

    return (
        db.query(Insurance)
        .join(Vehicle, Insurance.vehicle_id == Vehicle.vehicle_id)
        .join(Customer, Vehicle.customer_id == Customer.customer_id)
        .filter(Customer.user_id == current_user.id)
        .all()
    )


@router.get("/{insurance_id}", response_model=InsuranceResponse)
def get_insurance(
    insurance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    insurance = db.query(Insurance).filter(
        Insurance.insurance_id == insurance_id
    ).first()

    if not insurance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance policy not found"
        )

    if current_user.role != "admin" and insurance.vehicle.customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this insurance policy"
        )

    return insurance


@router.put("/{insurance_id}", response_model=InsuranceResponse)
def update_insurance(
    insurance_id: int,
    insurance_data: InsuranceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    insurance = db.query(Insurance).filter(
        Insurance.insurance_id == insurance_id
    ).first()

    if not insurance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance policy not found"
        )

    if current_user.role != "admin" and insurance.vehicle.customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to modify this insurance policy"
        )

    update_data = insurance_data.model_dump(exclude_unset=True)

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
                detail="Cannot transfer insurance to vehicle owned by another user"
            )

    if "policy_number" in update_data and update_data["policy_number"] is not None:
        existing_policy = db.query(Insurance).filter(
            Insurance.policy_number == update_data["policy_number"],
            Insurance.insurance_id != insurance_id
        ).first()

        if existing_policy:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Policy number already exists"
            )

    for field, value in update_data.items():
        setattr(insurance, field, value)

    db.commit()
    db.refresh(insurance)

    return insurance


@router.delete("/{insurance_id}")
def delete_insurance(
    insurance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    insurance = db.query(Insurance).filter(
        Insurance.insurance_id == insurance_id
    ).first()

    if not insurance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance policy not found"
        )

    if current_user.role != "admin" and insurance.vehicle.customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to delete this insurance policy"
        )

    db.delete(insurance)
    db.commit()

    return {"message": "Insurance policy deleted successfully"}
