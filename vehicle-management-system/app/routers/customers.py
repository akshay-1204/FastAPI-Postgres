from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_active_user
from app.models import Customer, User
from app.schemas import CustomerCreate, CustomerResponse, CustomerUpdate

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


@router.post(
    "/",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED
)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    target_user_id = current_user.id
    if current_user.role == "admin" and customer_data.user_id is not None:
        target_user_id = customer_data.user_id

    target_user = db.query(User).filter(User.id == target_user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated user account not found"
        )

    existing_link = db.query(Customer).filter(
        Customer.user_id == target_user_id
    ).first()

    if existing_link:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This user already has a customer record"
        )

    existing_customer = db.query(Customer).filter(
        (Customer.email == customer_data.email) |
        (Customer.phone == customer_data.phone)
    ).first()

    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer email or phone already exists"
        )

    new_customer = Customer(
        user_id=target_user_id,
        full_name=customer_data.full_name,
        email=customer_data.email,
        phone=customer_data.phone,
        address=customer_data.address
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer


@router.get("/", response_model=list[CustomerResponse])
def get_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    if current_user.role == "admin":
        return db.query(Customer).all()
    return db.query(Customer).filter(
        Customer.user_id == current_user.id
    ).all()


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    if current_user.role != "admin" and customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this customer record"
        )

    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    if current_user.role != "admin" and customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to modify this customer record"
        )

    update_data = customer_data.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] is not None:
        conflict = db.query(Customer).filter(
            Customer.email == update_data["email"],
            Customer.customer_id != customer_id
        ).first()
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already used by another customer"
            )

    if "phone" in update_data and update_data["phone"] is not None:
        conflict = db.query(Customer).filter(
            Customer.phone == update_data["phone"],
            Customer.customer_id != customer_id
        ).first()
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone is already used by another customer"
            )

    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)

    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_200_OK)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    if current_user.role != "admin" and customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to delete this customer record"
        )

    db.delete(customer)
    db.commit()

    return {"message": "Customer deleted successfully"}
