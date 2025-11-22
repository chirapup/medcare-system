from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Transfer, TransferCreate, TransferStatus, Patient, Hospital

router = APIRouter()


@router.post("/", status_code=201)
def create_transfer(transfer: TransferCreate, db: Session = Depends(get_db)):
    """Create a new transfer request"""
    # Validate patient exists
    patient = db.query(Patient).filter(Patient.id == transfer.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Validate hospitals exist
    from_hosp = db.query(Hospital).filter(Hospital.id == transfer.from_hospital_id).first()
    to_hosp = db.query(Hospital).filter(Hospital.id == transfer.to_hospital_id).first()

    if not from_hosp or not to_hosp:
        raise HTTPException(status_code=404, detail="One or both hospitals not found")

    # Check if destination hospital has capacity
    if to_hosp.available_beds <= 0:
        raise HTTPException(status_code=400, detail="Destination hospital has no available beds")

    db_transfer = Transfer(**transfer.dict())
    db.add(db_transfer)
    db.commit()
    db.refresh(db_transfer)
    return db_transfer


@router.get("/")
def get_transfers(
        status: Optional[str] = None,
        hospital_id: Optional[int] = None,
        db: Session = Depends(get_db)
):
    """Get all transfers with optional filters"""
    query = db.query(Transfer)

    if status:
        try:
            query = query.filter(Transfer.transfer_status == TransferStatus[status.upper()])
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid status")

    if hospital_id:
        query = query.filter(
            or_(
                Transfer.from_hospital_id == hospital_id,
                Transfer.to_hospital_id == hospital_id
            )
        )

    transfers = query.all()
    return transfers


@router.get("/{transfer_id}")
def get_transfer(transfer_id: int, db: Session = Depends(get_db)):
    """Get a specific transfer"""
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transfer


@router.put("/{transfer_id}/status")
def update_transfer_status(
        transfer_id: int,
        status: str,
        approved_by: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """Update transfer status"""
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")

    try:
        new_status = TransferStatus[status.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid status")

    transfer.transfer_status = new_status

    if new_status == TransferStatus.IN_PROGRESS and approved_by:
        transfer.approved_by = approved_by
        transfer.approved_at = datetime.utcnow()
    elif new_status == TransferStatus.COMPLETED:
        transfer.completed_at = datetime.utcnow()

        # Update patient location
        patient = db.query(Patient).filter(Patient.id == transfer.patient_id).first()
        if patient:
            patient.hospital_id = transfer.to_hospital_id

            # Update hospital capacities
            from_hosp = db.query(Hospital).filter(
                Hospital.id == transfer.from_hospital_id
            ).first()
            to_hosp = db.query(Hospital).filter(
                Hospital.id == transfer.to_hospital_id
            ).first()

            if from_hosp:
                from_hosp.available_beds += 1
            if to_hosp:
                to_hosp.available_beds -= 1

    db.commit()
    return {"message": "Transfer status updated", "status": status}


@router.get("/patient/{patient_id}")
def get_patient_transfers(patient_id: int, db: Session = Depends(get_db)):
    """Get all transfers for a specific patient"""
    transfers = db.query(Transfer).filter(Transfer.patient_id == patient_id).all()
    return transfers


@router.delete("/{transfer_id}")
def cancel_transfer(transfer_id: int, db: Session = Depends(get_db)):
    """Cancel a transfer request"""
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")

    if transfer.transfer_status == TransferStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Cannot cancel completed transfer")

    transfer.transfer_status = TransferStatus.CANCELLED
    db.commit()
    return {"message": "Transfer cancelled"}