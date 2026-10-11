from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from database import engine
import models
from routers import blogs, users

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(blogs.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Blog API"}