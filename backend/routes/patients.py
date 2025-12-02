from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Patient, PatientCreate, PatientResponse, TriageLevel, Hospital

router = APIRouter()

@router.post("/", response_model=PatientResponse, status_code=201)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """Create a new patient record with bed capacity validation"""
    # Check if MRN already exists
    existing = db.query(Patient).filter(Patient.mrn == patient.mrn).first()
    if existing:
        raise HTTPException(status_code=400, detail="Patient with this MRN already exists")
    
    # Validate hospital exists and has capacity
    hospital = db.query(Hospital).filter(Hospital.id == patient.hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    if hospital.available_beds <= 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Hospital '{hospital.name}' has no available beds. Current capacity: {hospital.capacity - hospital.available_beds}/{hospital.capacity}"
        )
    
    # Validate triage level
    try:
        triage = TriageLevel[patient.triage_level.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid triage level. Must be one of: {', '.join([t.name for t in TriageLevel])}"
        )
    
    # Create patient
    db_patient = Patient(**patient.dict())
    db_patient.triage_level = triage
    
    # Reduce hospital bed count
    hospital.available_beds -= 1
    
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
    """Get all patients with optional filters, sorted by triage priority"""
    query = db.query(Patient)
    
    if hospital_id:
        query = query.filter(Patient.hospital_id == hospital_id)
    if triage_level:
        try:
            triage = TriageLevel[triage_level.upper()]
            query = query.filter(Patient.triage_level == triage)
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid triage level")
    
    # Sort by triage priority (CRITICAL first)
    triage_order = {
        TriageLevel.CRITICAL: 1,
        TriageLevel.URGENT: 2,
        TriageLevel.SEMI_URGENT: 3,
        TriageLevel.NON_URGENT: 4
    }
    
    patients = query.offset(skip).limit(limit).all()
    patients.sort(key=lambda p: triage_order.get(p.triage_level, 999))
    
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
    updated_by: str,
    db: Session = Depends(get_db)
):
    """Update patient triage level with validation and audit trail"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Validate triage level
    try:
        new_triage = TriageLevel[triage_level.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid triage level. Must be one of: {', '.join([t.name for t in TriageLevel])}"
        )
    
    old_triage = patient.triage_level
    patient.triage_level = new_triage
    patient.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Triage level updated",
        "patient_id": patient_id,
        "old_triage": str(old_triage),
        "new_triage": str(new_triage),
        "updated_by": updated_by,
        "updated_at": datetime.utcnow().isoformat()
    }

@router.delete("/{patient_id}")
def discharge_patient(
    patient_id: int, 
    discharged_by: str,
    db: Session = Depends(get_db)
):
    """Discharge a patient and free up hospital bed"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Free up the bed in the hospital
    hospital = db.query(Hospital).filter(Hospital.id == patient.hospital_id).first()
    if hospital:
        hospital.available_beds += 1
    
    patient_info = {
        "mrn": patient.mrn,
        "name": f"{patient.first_name} {patient.last_name}",
        "hospital_id": patient.hospital_id,
        "discharged_by": discharged_by,
        "discharged_at": datetime.utcnow().isoformat()
    }
    
    db.delete(patient)
    db.commit()
    
    return {
        "message": "Patient discharged successfully",
        "patient": patient_info
    }

@router.get("/stats/triage-distribution")
def get_triage_stats(db: Session = Depends(get_db)):
    """Get distribution of patients by triage level"""
    stats = db.query(
        Patient.triage_level,
        func.count(Patient.id).label('count')
    ).group_by(Patient.triage_level).all()
    
    return [{"triage_level": str(s[0]), "count": s[1]} for s in stats]

@router.get("/critical/list")
def get_critical_patients(db: Session = Depends(get_db)):
    """Get all critical patients - priority view"""
    critical_patients = db.query(Patient).filter(
        Patient.triage_level == TriageLevel.CRITICAL
    ).all()
    
    return {
        "count": len(critical_patients),
        "patients": critical_patients
    }
