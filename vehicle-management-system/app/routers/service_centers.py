from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_active_user, get_current_admin
from app.models import ServiceCenter, User
from app.schemas import (
    ServiceCenterCreate,
    ServiceCenterResponse,
    ServiceCenterUpdate,
)

router = APIRouter(
    prefix="/service-centers",
    tags=["Service Centers"]
)


@router.post(
    "/",
    response_model=ServiceCenterResponse,
    status_code=status.HTTP_201_CREATED
)
def create_service_center(
    center_data: ServiceCenterCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    new_center = ServiceCenter(
        center_name=center_data.center_name,
        phone=center_data.phone,
        email=center_data.email,
        address=center_data.address,
        city=center_data.city,
        rating=center_data.rating
    )

    db.add(new_center)
    db.commit()
    db.refresh(new_center)

    return new_center


@router.get("/", response_model=list[ServiceCenterResponse])
def get_service_centers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    return db.query(ServiceCenter).all()


@router.get("/{service_center_id}", response_model=ServiceCenterResponse)
def get_service_center(
    service_center_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    center = db.query(ServiceCenter).filter(
        ServiceCenter.service_center_id == service_center_id
    ).first()

    if not center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service center not found"
        )

    return center


@router.put("/{service_center_id}", response_model=ServiceCenterResponse)
def update_service_center(
    service_center_id: int,
    center_data: ServiceCenterUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    center = db.query(ServiceCenter).filter(
        ServiceCenter.service_center_id == service_center_id
    ).first()

    if not center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service center not found"
        )

    update_data = center_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(center, field, value)

    db.commit()
    db.refresh(center)

    return center


@router.delete("/{service_center_id}")
def delete_service_center(
    service_center_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    center = db.query(ServiceCenter).filter(
        ServiceCenter.service_center_id == service_center_id
    ).first()

    if not center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service center not found"
        )

    db.delete(center)
    db.commit()

    return {"message": "Service center deleted successfully"}
