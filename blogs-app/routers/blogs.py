from fastapi import Depends, status, HTTPException, APIRouter
from pydantic import BaseModel
from typing import Optional

from sqlalchemy.orm import Session
from db import get_db
import models
from schemas import UserResponse

router = APIRouter(
    prefix='/blogs',
    tags=['blogs']
)

class Blog(BaseModel):
    title: str
    content: str
    is_published: Optional[bool] = True
    user_id: int


class BlogResponse(BaseModel):
    title: str
    content: str
    is_published: Optional[bool] = True
    user_id: int
    user: UserResponse

@router.get('/', response_model=list[BlogResponse])
def get_blogs(db: Session = Depends(get_db)):
        return db.query(models.Blog).all()

@router.post('/')
def create_blog(blog: Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(**blog.model_dump())
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@router.get('/{id}', response_model=BlogResponse)
def get_blogs(id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).get(id)
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Blog not found')
    else:
        return blog

@router.put('/{id}')
def update_blog(id: int, payload: Blog, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).get(id)
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Blog not found')
    else:
        cpayload = payload.model_dump(exclude_unset=True)

        for key, value in cpayload.items():
            setattr(blog, key, value)
        db.commit()
        db.refresh(blog)
        return blog

@router.delete('/{id}')
def delete_blog(id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).get(id)
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Blog not found')
    else:
        db.delete(blog)
        db.commit()
        return {
            'message': 'Deleted blog successfully'
        }