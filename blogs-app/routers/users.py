from datetime import datetime
from fastapi import Depends, status, HTTPException, APIRouter
from pydantic import BaseModel

from sqlalchemy.orm import Session
from db import get_db
import models
import utils

router = APIRouter(
    prefix='/users',
    tags=['users']
)

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    password: str
    created_at: datetime
    updated_at: datetime

from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

oauth2_schema = OAuth2PasswordBearer(tokenUrl='login')

def get_current_user(token: str = Depends(oauth2_schema)):
    try:
        payload = jwt.decode(token, "You can't steel my app", algorithms=['HS256'])
        return payload['id']
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token is invalid or expired'
        )

@router.get('/', response_model=list[UserResponse], status_code=status.HTTP_200_OK)
def get_users(db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    return db.query(models.User).all()

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exist')
    else:
        hashed_password = utils.hash_password(payload.password)
        payload_dict = payload.model_dump()
        payload_dict['password'] = hashed_password
        user = models.User(**payload_dict)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

@router.post('/login', status_code=status.HTTP_200_OK)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if user:
        is_password_valid = utils.verify_password(payload.password, user.password)
        if is_password_valid:
            access_token = utils.create_access_token(
                {
                    'email': user.email,
                    'id': user.id
                }
            )

            return {
                'token': access_token,
                'id': user.id
            }
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Incorrect password')

    else:   
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Incorrect email address')
