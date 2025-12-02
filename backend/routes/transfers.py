from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Transfer, TransferCreate, TransferStatus, Patient, Hospital, TriageLevel

router = APIRouter()

@router.post("/", status_code=201)
def create_transfer(transfer: TransferCreate, db: Session = Depends(get_db)):
    """Create a new transfer request with full validation"""
    
    # 1. Validate patient exists and belongs to source hospital
    patient = db.query(Patient).filter(Patient.id == transfer.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    if patient.hospital_id != transfer.from_hospital_id:
        raise HTTPException(
            status_code=400,
            detail=f"Patient is not at source hospital. Patient is currently at hospital {patient.hospital_id}"
        )
    
    # 2. Validate hospitals exist
    from_hosp = db.query(Hospital).filter(Hospital.id == transfer.from_hospital_id).first()
    to_hosp = db.query(Hospital).filter(Hospital.id == transfer.to_hospital_id).first()
    
    if not from_hosp or not to_hosp:
        raise HTTPException(status_code=404, detail="One or both hospitals not found")
    
    # 3. Validate different hospitals
    if transfer.from_hospital_id == transfer.to_hospital_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot transfer patient to the same hospital"
        )
    
    # 4. Check if destination hospital has capacity
    if to_hosp.available_beds <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"Destination hospital '{to_hosp.name}' has no available beds. Capacity: {to_hosp.capacity - to_hosp.available_beds}/{to_hosp.capacity}"
        )
    
    # 5. Check for pending transfers for this patient
    existing_transfer = db.query(Transfer).filter(
        Transfer.patient_id == transfer.patient_id,
        or_(
            Transfer.transfer_status == TransferStatus.PENDING,
            Transfer.transfer_status == TransferStatus.IN_PROGRESS
        )
    ).first()
    
    if existing_transfer:
        raise HTTPException(
            status_code=400,
            detail=f"Patient already has an active transfer (ID: {existing_transfer.id}, Status: {existing_transfer.transfer_status})"
        )
    
    # 6. Validate priority level
    try:
        priority = TriageLevel[transfer.priority.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority level. Must be one of: {', '.join([t.name for t in TriageLevel])}"
        )
    
    # 7. Create transfer
    db_transfer = Transfer(**transfer.dict())
    db_transfer.priority = priority
    db_transfer.transfer_status = TransferStatus.PENDING
    
    db.add(db_transfer)
    db.commit()
    db.refresh(db_transfer)
    
    return {
        "transfer": db_transfer,
        "message": f"Transfer request created. Patient will be moved from {from_hosp.name} to {to_hosp.name}",
        "destination_available_beds": to_hosp.available_beds
    }

@router.get("/")
def get_transfers(
    status: Optional[str] = None,
    hospital_id: Optional[int] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all transfers with optional filters, sorted by priority"""
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
    
    if priority:
        try:
            query = query.filter(Transfer.priority == TriageLevel[priority.upper()])
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid priority")
    
    # Sort by priority (CRITICAL first) and then by requested time
    transfers = query.all()
    priority_order = {
        TriageLevel.CRITICAL: 1,
        TriageLevel.URGENT: 2,
        TriageLevel.SEMI_URGENT: 3,
        TriageLevel.NON_URGENT: 4
    }
    transfers.sort(key=lambda t: (priority_order.get(t.priority, 999), t.requested_at))
    
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
    approved_by: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update transfer status with full workflow enforcement"""
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    
    # Validate status transition
    try:
        new_status = TransferStatus[status.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    # Enforce status workflow
    valid_transitions = {
        TransferStatus.PENDING: [TransferStatus.IN_PROGRESS, TransferStatus.CANCELLED],
        TransferStatus.IN_PROGRESS: [TransferStatus.COMPLETED, TransferStatus.CANCELLED],
        TransferStatus.COMPLETED: [],  # Cannot change from completed
        TransferStatus.CANCELLED: []   # Cannot change from cancelled
    }
    
    if new_status not in valid_transitions.get(transfer.transfer_status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {transfer.transfer_status} to {new_status}"
        )
    
    # Update transfer
    old_status = transfer.transfer_status
    transfer.transfer_status = new_status
    
    if notes:
        transfer.notes = (transfer.notes or "") + f"\n[{datetime.utcnow()}] {approved_by}: {notes}"
    
    if new_status == TransferStatus.IN_PROGRESS:
        transfer.approved_by = approved_by
        transfer.approved_at = datetime.utcnow()
        
        # Validate capacity still available
        to_hosp = db.query(Hospital).filter(Hospital.id == transfer.to_hospital_id).first()
        if to_hosp.available_beds <= 0:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Destination hospital no longer has available beds"
            )
    
    elif new_status == TransferStatus.COMPLETED:
        transfer.completed_at = datetime.utcnow()
        
        # Update patient location
        patient = db.query(Patient).filter(Patient.id == transfer.patient_id).first()
        if not patient:
            db.rollback()
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Validate patient is still at source hospital
        if patient.hospital_id != transfer.from_hospital_id:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Patient is no longer at source hospital"
            )
        
        # Update hospital capacities
        from_hosp = db.query(Hospital).filter(Hospital.id == transfer.from_hospital_id).first()
        to_hosp = db.query(Hospital).filter(Hospital.id == transfer.to_hospital_id).first()
        
        if not from_hosp or not to_hosp:
            db.rollback()
            raise HTTPException(status_code=404, detail="Hospital not found")
        
        # Final capacity check
        if to_hosp.available_beds <= 0:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Destination hospital has no available beds"
            )
        
        # Execute the transfer
        patient.hospital_id = transfer.to_hospital_id
        patient.updated_at = datetime.utcnow()
        from_hosp.available_beds += 1
        to_hosp.available_beds -= 1
    
    elif new_status == TransferStatus.CANCELLED:
        # No capacity changes needed for cancellation
        pass
    
    db.commit()
    
    return {
        "message": f"Transfer status updated from {old_status} to {new_status}",
        "transfer_id": transfer_id,
        "status": new_status,
        "approved_by": approved_by,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/patient/{patient_id}")
def get_patient_transfers(patient_id: int, db: Session = Depends(get_db)):
    """Get all transfers for a specific patient"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    transfers = db.query(Transfer).filter(Transfer.patient_id == patient_id).order_by(Transfer.requested_at.desc()).all()
    
    return {
        "patient_id": patient_id,
        "patient_name": f"{patient.first_name} {patient.last_name}",
        "mrn": patient.mrn,
        "total_transfers": len(transfers),
        "transfers": transfers
    }

@router.delete("/{transfer_id}")
def cancel_transfer(
    transfer_id: int,
    cancelled_by: str,
    reason: str,
    db: Session = Depends(get_db)
):
    """Cancel a transfer request with reason"""
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    
    if transfer.transfer_status == TransferStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Cannot cancel completed transfer")
    
    if transfer.transfer_status == TransferStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Transfer already cancelled")
    
    transfer.transfer_status = TransferStatus.CANCELLED
    transfer.notes = (transfer.notes or "") + f"\n[{datetime.utcnow()}] Cancelled by {cancelled_by}: {reason}"
    
    db.commit()
    
    return {
        "message": "Transfer cancelled",
        "transfer_id": transfer_id,
        "cancelled_by": cancelled_by,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/pending/priority")
def get_pending_by_priority(db: Session = Depends(get_db)):
    """Get all pending transfers sorted by priority for dispatch"""
    pending = db.query(Transfer).filter(
        Transfer.transfer_status == TransferStatus.PENDING
    ).all()
    
    # Sort by priority
    priority_order = {
        TriageLevel.CRITICAL: 1,
        TriageLevel.URGENT: 2,
        TriageLevel.SEMI_URGENT: 3,
        TriageLevel.NON_URGENT: 4
    }
    pending.sort(key=lambda t: (priority_order.get(t.priority, 999), t.requested_at))
    
    return {
        "total_pending": len(pending),
        "critical_count": sum(1 for t in pending if t.priority == TriageLevel.CRITICAL),
        "transfers": pending
    }
