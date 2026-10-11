from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_active_user
from app.models import (
    Customer,
    Insurance,
    ServiceCenter,
    ServiceRecord,
    User,
    Vehicle,
    VehiclePart,
)

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.get("/vehicles-by-type")
def vehicles_by_type(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    query = db.query(
        Vehicle.vehicle_type,
        func.count(Vehicle.vehicle_id).label("total_vehicles")
    )

    if current_user.role != "admin":
        query = query.join(
            Customer, Vehicle.customer_id == Customer.customer_id
        ).filter(Customer.user_id == current_user.id)

    results = query.group_by(Vehicle.vehicle_type).all()

    return [
        {
            "vehicle_type": row.vehicle_type,
            "total_vehicles": row.total_vehicles
        }
        for row in results
    ]


@router.get("/service-cost-summary")
def service_cost_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    query = db.query(
        func.count(ServiceRecord.service_id).label("total_services"),
        func.coalesce(
            func.sum(ServiceRecord.service_cost), 0
        ).label("total_service_cost"),
        func.coalesce(
            func.avg(ServiceRecord.service_cost), 0
        ).label("average_service_cost")
    )

    if current_user.role != "admin":
        query = (
            query.join(Vehicle, ServiceRecord.vehicle_id == Vehicle.vehicle_id)
            .join(Customer, Vehicle.customer_id == Customer.customer_id)
            .filter(Customer.user_id == current_user.id)
        )

    results = query.first()

    return {
        "total_services": results.total_services if results else 0,
        "total_service_cost": results.total_service_cost if results else 0,
        "average_service_cost": results.average_service_cost if results else 0
    }


@router.get("/customer-vehicles")
def customer_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    query = db.query(
        Customer.customer_id,
        Customer.full_name,
        func.count(Vehicle.vehicle_id).label("total_vehicles")
    ).outerjoin(
        Vehicle,
        Customer.customer_id == Vehicle.customer_id
    )

    if current_user.role != "admin":
        query = query.filter(Customer.user_id == current_user.id)

    results = (
        query.group_by(
            Customer.customer_id,
            Customer.full_name
        ).all()
    )

    return [
        {
            "customer_id": row.customer_id,
            "customer_name": row.full_name,
            "total_vehicles": row.total_vehicles
        }
        for row in results
    ]


@router.get("/top-service-centers")
def top_service_centers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    query = (
        db.query(
            ServiceCenter.service_center_id,
            ServiceCenter.center_name,
            func.count(ServiceRecord.service_id).label("total_services"),
            func.coalesce(
                func.sum(ServiceRecord.service_cost), 0
            ).label("total_revenue")
        )
        .outerjoin(
            ServiceRecord,
            ServiceCenter.service_center_id == ServiceRecord.service_center_id
        )
    )

    if current_user.role != "admin":
        query = (
            query.join(Vehicle, ServiceRecord.vehicle_id == Vehicle.vehicle_id)
            .join(Customer, Vehicle.customer_id == Customer.customer_id)
            .filter(Customer.user_id == current_user.id)
        )

    results = (
        query.group_by(
            ServiceCenter.service_center_id,
            ServiceCenter.center_name
        )
        .having(func.count(ServiceRecord.service_id) > 0)
        .order_by(func.count(ServiceRecord.service_id).desc())
        .all()
    )

    return [
        {
            "service_center_id": row.service_center_id,
            "center_name": row.center_name,
            "total_services": row.total_services,
            "total_revenue": row.total_revenue
        }
        for row in results
    ]


@router.get("/vehicle-service-history/{vehicle_id}")
def vehicle_service_history(
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
            detail="Access denied to this vehicle history"
        )

    results = (
        db.query(
            ServiceRecord.service_id,
            ServiceRecord.service_date,
            ServiceRecord.service_type,
            ServiceRecord.service_cost,
            ServiceCenter.center_name
        )
        .join(
            ServiceCenter,
            ServiceRecord.service_center_id == ServiceCenter.service_center_id
        )
        .filter(ServiceRecord.vehicle_id == vehicle_id)
        .order_by(ServiceRecord.service_date.desc())
        .all()
    )

    return [
        {
            "service_id": row.service_id,
            "service_date": row.service_date,
            "service_type": row.service_type,
            "service_cost": row.service_cost,
            "service_center": row.center_name
        }
        for row in results
    ]


@router.get("/parts-cost-summary")
def parts_cost_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    query = db.query(
        func.count(VehiclePart.part_id).label("total_parts"),
        func.coalesce(
            func.sum(VehiclePart.quantity), 0
        ).label("total_quantity"),
        func.coalesce(
            func.sum(VehiclePart.total_price), 0
        ).label("total_parts_cost")
    )

    if current_user.role != "admin":
        query = (
            query.join(ServiceRecord, VehiclePart.service_id == ServiceRecord.service_id)
            .join(Vehicle, ServiceRecord.vehicle_id == Vehicle.vehicle_id)
            .join(Customer, Vehicle.customer_id == Customer.customer_id)
            .filter(Customer.user_id == current_user.id)
        )

    results = query.first()

    return {
        "total_parts": results.total_parts if results else 0,
        "total_quantity": results.total_quantity if results else 0,
        "total_parts_cost": results.total_parts_cost if results else 0
    }


@router.get("/insurance-status")
def insurance_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    query = db.query(
        Insurance.status,
        func.count(Insurance.insurance_id).label("total_policies")
    )

    if current_user.role != "admin":
        query = (
            query.join(Vehicle, Insurance.vehicle_id == Vehicle.vehicle_id)
            .join(Customer, Vehicle.customer_id == Customer.customer_id)
            .filter(Customer.user_id == current_user.id)
        )

    results = query.group_by(Insurance.status).all()

    return [
        {
            "status": row.status,
            "total_policies": row.total_policies
        }
        for row in results
    ]
