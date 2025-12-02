from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base

class TriageLevel(enum.Enum):
    CRITICAL = "critical"
    URGENT = "urgent"
    SEMI_URGENT = "semi-urgent"
    NON_URGENT = "non-urgent"

class TransferStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Hospital(Base):
    __tablename__ = "hospitals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    capacity = Column(Integer)
    available_beds = Column(Integer)
    phone = Column(String(20))
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patients = relationship("Patient", back_populates="hospital")
    transfers_from = relationship("Transfer", foreign_keys="Transfer.from_hospital_id", back_populates="from_hospital")
    transfers_to = relationship("Transfer", foreign_keys="Transfer.to_hospital_id", back_populates="to_hospital")

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    mrn = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime)
    gender = Column(String(20))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(String(500))
    emergency_contact = Column(String(200))
    emergency_phone = Column(String(20))
    
    # Medical Info
    blood_type = Column(String(10))
    allergies = Column(Text)
    current_medications = Column(Text)
    medical_history = Column(Text)
    
    # Current Status
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    triage_level = Column(Enum(TriageLevel))
    admission_date = Column(DateTime, default=datetime.utcnow)
    current_diagnosis = Column(Text)
    attending_physician = Column(String(200))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    hospital = relationship("Hospital", back_populates="patients")
    transfers = relationship("Transfer", back_populates="patient")

class Transfer(Base):
    __tablename__ = "transfers"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    from_hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    to_hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    
    transfer_reason = Column(Text, nullable=False)
    transfer_status = Column(Enum(TransferStatus), default=TransferStatus.PENDING)
    priority = Column(Enum(TriageLevel))
    
    requested_by = Column(String(200))
    approved_by = Column(String(200))
    
    requested_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    notes = Column(Text)
    documents_transferred = Column(Text)
    
    patient = relationship("Patient", back_populates="transfers")
    from_hospital = relationship("Hospital", foreign_keys=[from_hospital_id], back_populates="transfers_from")
    to_hospital = relationship("Hospital", foreign_keys=[to_hospital_id], back_populates="transfers_to")

# Pydantic schemas for API
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime as dt

class PatientCreate(BaseModel):
    mrn: str
    first_name: str
    last_name: str
    date_of_birth: dt
    gender: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    hospital_id: int
    triage_level: str  # Will be validated in route to enum
    
    class Config:
        json_schema_extra = {
            "example": {
                "mrn": "MRN12345",
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1985-05-15T00:00:00",
                "gender": "Male",
                "phone": "408-555-1234",
                "email": "john.doe@email.com",
                "blood_type": "O+",
                "allergies": "Penicillin",
                "hospital_id": 1,
                "triage_level": "URGENT"
            }
        }

class PatientResponse(BaseModel):
    id: int
    mrn: str
    first_name: str
    last_name: str
    triage_level: Optional[str]
    hospital_id: int
    admission_date: dt
    
    class Config:
        from_attributes = True

class HospitalCreate(BaseModel):
    name: str
    address: str
    city: str
    state: str
    capacity: int
    available_beds: int

class TransferCreate(BaseModel):
    patient_id: int
    from_hospital_id: int
    to_hospital_id: int
    transfer_reason: str
    priority: str
    requested_by: str
