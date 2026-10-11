from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import (
    auth,
    customers,
    insurance,
    reports,
    service_centers,
    service_records,
    vehicle_parts,
    vehicles,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Vehicle Management System API",
    version="2.0.0",
    description="Secure, role-aware Vehicle Management API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(vehicles.router)
app.include_router(insurance.router)
app.include_router(service_centers.router)
app.include_router(service_records.router)
app.include_router(vehicle_parts.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to the Secure Vehicle Management System API",
        "version": "2.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
