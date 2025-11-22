from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Patient, PatientCreate, PatientResponse, TriageLevel

router = APIRouter()


@router.post("/", response_model=PatientResponse, status_code=201)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """Create a new patient record"""
    # Check if MRN already exists
    existing = db.query(Patient).filter(Patient.mrn == patient.mrn).first()
    if existing:
        raise HTTPException(status_code=400, detail="Patient with this MRN already exists")

    db_patient = Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@router.get("/", response_model=List[PatientResponse])
def get_patients(
        skip: int = 0,
        limit: int = 100,
        hospital_id: Optional[int] = None,
        triage_level: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """Get all patients with optional filters"""
    query = db.query(Patient)

    if hospital_id:
        query = query.filter(Patient.hospital_id == hospital_id)
    if triage_level:
        query = query.filter(Patient.triage_level == triage_level)

    patients = query.offset(skip).limit(limit).all()
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Get a specific patient by ID"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.get("/mrn/{mrn}", response_model=PatientResponse)
def get_patient_by_mrn(mrn: str, db: Session = Depends(get_db)):
    """Get a patient by Medical Record Number"""
    patient = db.query(Patient).filter(Patient.mrn == mrn).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.put("/{patient_id}/triage")
def update_triage(
        patient_id: int,
        triage_level: str,
        db: Session = Depends(get_db)
):
    """Update patient triage level"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    try:
        patient.triage_level = TriageLevel[triage_level.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid triage level")

    patient.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Triage level updated", "patient_id": patient_id}


@router.delete("/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """Delete a patient record"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db.delete(patient)
    db.commit()
    return {"message": "Patient deleted successfully"}


@router.get("/stats/triage-distribution")
def get_triage_stats(db: Session = Depends(get_db)):
    """Get distribution of patients by triage level"""
    stats = db.query(
        Patient.triage_level,
        func.count(Patient.id).label('count')
    ).group_by(Patient.triage_level).all()

    return [{"triage_level": str(s[0]), "count": s[1]} for s in stats]