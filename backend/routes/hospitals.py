from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from database import get_db
from models import Hospital, HospitalCreate, Patient

router = APIRouter()


@router.post("/", status_code=201)
def create_hospital(hospital: HospitalCreate, db: Session = Depends(get_db)):
    """Create a new hospital"""
    db_hospital = Hospital(**hospital.dict())
    db.add(db_hospital)
    db.commit()
    db.refresh(db_hospital)
    return db_hospital


@router.get("/")
def get_hospitals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all hospitals"""
    hospitals = db.query(Hospital).offset(skip).limit(limit).all()
    return hospitals


@router.get("/{hospital_id}")
def get_hospital(hospital_id: int, db: Session = Depends(get_db)):
    """Get a specific hospital"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital


@router.get("/{hospital_id}/patients")
def get_hospital_patients(hospital_id: int, db: Session = Depends(get_db)):
    """Get all patients in a hospital"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    patients = db.query(Patient).filter(Patient.hospital_id == hospital_id).all()
    return patients


@router.put("/{hospital_id}/capacity")
def update_capacity(
        hospital_id: int,
        available_beds: int,
        db: Session = Depends(get_db)
):
    """Update hospital bed availability"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    if available_beds > hospital.capacity:
        raise HTTPException(
            status_code=400,
            detail="Available beds cannot exceed total capacity"
        )

    hospital.available_beds = available_beds
    db.commit()
    return {"message": "Capacity updated", "available_beds": available_beds}


@router.get("/{hospital_id}/stats")
def get_hospital_stats(hospital_id: int, db: Session = Depends(get_db)):
    """Get hospital statistics"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    total_patients = db.query(func.count(Patient.id)).filter(
        Patient.hospital_id == hospital_id
    ).scalar()

    occupancy_rate = (total_patients / hospital.capacity * 100) if hospital.capacity > 0 else 0

    return {
        "hospital_id": hospital_id,
        "hospital_name": hospital.name,
        "total_capacity": hospital.capacity,
        "available_beds": hospital.available_beds,
        "current_patients": total_patients,
        "occupancy_rate": round(occupancy_rate, 2)
    }