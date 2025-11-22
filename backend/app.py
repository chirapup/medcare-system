from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uvicorn

from database import engine, get_db, Base
from models import Patient, Hospital, Transfer, TransferStatus
from routes import patients, hospitals, transfers

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MedCare System API",
    description="Patient-Hospital Workflow Optimization Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(patients.router, prefix="/api/patients", tags=["Patients"])
app.include_router(hospitals.router, prefix="/api/hospitals", tags=["Hospitals"])
app.include_router(transfers.router, prefix="/api/transfers", tags=["Transfers"])

@app.get("/")
def root():
    return {
        "message": "MedCare System API",
        "version": "1.0.0",
        "endpoints": {
            "patients": "/api/patients",
            "hospitals": "/api/hospitals",
            "transfers": "/api/transfers",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)