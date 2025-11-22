# MedCare System - API Examples

Complete guide to using the MedCare System API with example requests and responses.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. For production use, implement JWT tokens or OAuth2.

---

## 🏥 Hospitals API

### List All Hospitals

```bash
GET /api/hospitals/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "San Jose Medical Center",
    "address": "123 Hospital Ave",
    "city": "San Jose",
    "state": "CA",
    "zip_code": null,
    "capacity": 150,
    "available_beds": 75,
    "phone": null,
    "email": null,
    "created_at": "2024-01-15T10:30:00"
  }
]
```

### Create Hospital

```bash
POST /api/hospitals/
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Stanford Health Care",
  "address": "300 Pasteur Dr",
  "city": "Palo Alto",
  "state": "CA",
  "capacity": 200,
  "available_beds": 100
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "name": "Stanford Health Care",
  "address": "300 Pasteur Dr",
  "city": "Palo Alto",
  "state": "CA",
  "capacity": 200,
  "available_beds": 100,
  "created_at": "2024-01-15T10:35:00"
}
```

### Get Hospital by ID

```bash
GET /api/hospitals/1
```

### Get Hospital Patients

```bash
GET /api/hospitals/1/patients
```

### Get Hospital Statistics

```bash
GET /api/hospitals/1/stats
```

**Response:**
```json
{
  "hospital_id": 1,
  "hospital_name": "San Jose Medical Center",
  "total_capacity": 150,
  "available_beds": 75,
  "current_patients": 75,
  "occupancy_rate": 50.0
}
```

### Update Hospital Capacity

```bash
PUT /api/hospitals/1/capacity?available_beds=80
```

**Response:**
```json
{
  "message": "Capacity updated",
  "available_beds": 80
}
```

---

## 👥 Patients API

### List All Patients

```bash
GET /api/patients/?limit=100
```

**Optional Query Parameters:**
- `skip`: Number of records to skip (pagination)
- `limit`: Maximum number of records to return
- `hospital_id`: Filter by hospital
- `triage_level`: Filter by triage level (CRITICAL, URGENT, SEMI_URGENT, NON_URGENT)

**Example:**
```bash
GET /api/patients/?hospital_id=1&triage_level=URGENT
```

### Create Patient

```bash
POST /api/patients/
Content-Type: application/json
```

**Request Body:**
```json
{
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
```

**Response (201 Created):**
```json
{
  "id": 1,
  "mrn": "MRN12345",
  "first_name": "John",
  "last_name": "Doe",
  "triage_level": "URGENT",
  "hospital_id": 1,
  "admission_date": "2024-01-15T10:40:00"
}
```

### Get Patient by ID

```bash
GET /api/patients/1
```

### Get Patient by MRN

```bash
GET /api/patients/mrn/MRN12345
```

### Update Patient Triage Level

```bash
PUT /api/patients/1/triage?triage_level=CRITICAL
```

**Response:**
```json
{
  "message": "Triage level updated",
  "patient_id": 1
}
```

### Delete Patient

```bash
DELETE /api/patients/1
```

**Response:**
```json
{
  "message": "Patient deleted successfully"
}
```

### Get Triage Statistics

```bash
GET /api/patients/stats/triage-distribution
```

**Response:**
```json
[
  {
    "triage_level": "CRITICAL",
    "count": 5
  },
  {
    "triage_level": "URGENT",
    "count": 15
  },
  {
    "triage_level": "SEMI_URGENT",
    "count": 25
  },
  {
    "triage_level": "NON_URGENT",
    "count": 30
  }
]
```

---

## 🚑 Transfers API

### List All Transfers

```bash
GET /api/transfers/
```

**Optional Query Parameters:**
- `status`: Filter by status (PENDING, IN_PROGRESS, COMPLETED, CANCELLED)
- `hospital_id`: Filter by source or destination hospital

**Example:**
```bash
GET /api/transfers/?status=PENDING
GET /api/transfers/?hospital_id=1
```

### Create Transfer Request

```bash
POST /api/transfers/
Content-Type: application/json
```

**Request Body:**
```json
{
  "patient_id": 1,
  "from_hospital_id": 1,
  "to_hospital_id": 2,
  "transfer_reason": "Requires specialized cardiac care",
  "priority": "URGENT",
  "requested_by": "Dr. Smith"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "patient_id": 1,
  "from_hospital_id": 1,
  "to_hospital_id": 2,
  "transfer_reason": "Requires specialized cardiac care",
  "transfer_status": "PENDING",
  "priority": "URGENT",
  "requested_by": "Dr. Smith",
  "requested_at": "2024-01-15T10:45:00"
}
```

### Get Transfer by ID

```bash
GET /api/transfers/1
```

### Update Transfer Status

```bash
PUT /api/transfers/1/status?status=IN_PROGRESS&approved_by=Dr.%20Johnson
```

**Response:**
```json
{
  "message": "Transfer status updated",
  "status": "IN_PROGRESS"
}
```

**Complete Transfer:**
```bash
PUT /api/transfers/1/status?status=COMPLETED
```

This will automatically:
- Update patient's hospital_id to destination hospital
- Increase source hospital's available beds
- Decrease destination hospital's available beds
- Set completion timestamp

### Get Patient Transfer History

```bash
GET /api/transfers/patient/1
```

### Cancel Transfer

```bash
DELETE /api/transfers/1
```

**Response:**
```json
{
  "message": "Transfer cancelled"
}
```

---

## 🔍 Common Use Cases

### Use Case 1: Admit New Patient

```bash
# 1. Create patient
POST /api/patients/
{
  "mrn": "MRN99999",
  "first_name": "Jane",
  "last_name": "Smith",
  "date_of_birth": "1990-08-20T00:00:00",
  "gender": "Female",
  "hospital_id": 1,
  "triage_level": "SEMI_URGENT"
}

# 2. Check hospital capacity
GET /api/hospitals/1/stats
```

### Use Case 2: Complete Patient Transfer

```bash
# 1. Create transfer request
POST /api/transfers/
{
  "patient_id": 1,
  "from_hospital_id": 1,
  "to_hospital_id": 2,
  "transfer_reason": "Need ICU",
  "priority": "CRITICAL",
  "requested_by": "Dr. Brown"
}

# 2. Approve transfer
PUT /api/transfers/1/status?status=IN_PROGRESS&approved_by=Dr.%20Chen

# 3. Complete transfer
PUT /api/transfers/1/status?status=COMPLETED

# 4. Verify patient location
GET /api/patients/1
```

### Use Case 3: Monitor Hospital Capacity

```bash
# Get all hospitals with capacity info
GET /api/hospitals/

# Get detailed stats for specific hospital
GET /api/hospitals/1/stats

# Get all critical patients
GET /api/patients/?triage_level=CRITICAL

# Get triage distribution across all patients
GET /api/patients/stats/triage-distribution
```

---

## 🐛 Error Responses

### 400 Bad Request
```json
{
  "detail": "Patient with this MRN already exists"
}
```

### 404 Not Found
```json
{
  "detail": "Patient not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "hospital_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## 📝 Enum Values Reference

### Triage Levels
- `CRITICAL` - Life-threatening condition
- `URGENT` - Serious condition requiring prompt attention
- `SEMI_URGENT` - Stable but requires timely care
- `NON_URGENT` - Minor condition

### Transfer Status
- `PENDING` - Awaiting approval
- `IN_PROGRESS` - Approved and in transit
- `COMPLETED` - Successfully transferred
- `CANCELLED` - Request cancelled

---

## 🔧 Testing with cURL

### Create Complete Workflow
```bash
# 1. Create two hospitals
curl -X POST http://localhost:8000/api/hospitals/ \
  -H "Content-Type: application/json" \
  -d '{"name":"City Hospital","address":"123 Main","city":"San Jose","state":"CA","capacity":100,"available_beds":50}'

curl -X POST http://localhost:8000/api/hospitals/ \
  -H "Content-Type: application/json" \
  -d '{"name":"County Hospital","address":"456 Oak","city":"Palo Alto","state":"CA","capacity":150,"available_beds":75}'

# 2. Create patient
curl -X POST http://localhost:8000/api/patients/ \
  -H "Content-Type: application/json" \
  -d '{"mrn":"TEST001","first_name":"Test","last_name":"Patient","date_of_birth":"1980-01-01T00:00:00","gender":"Male","hospital_id":1,"triage_level":"URGENT"}'

# 3. Create transfer
curl -X POST http://localhost:8000/api/transfers/ \
  -H "Content-Type: application/json" \
  -d '{"patient_id":1,"from_hospital_id":1,"to_hospital_id":2,"transfer_reason":"Test transfer","priority":"URGENT","requested_by":"Dr. Test"}'
```

---

## 💡 Tips

1. **Use the interactive docs** at `/docs` for easy testing
2. **Check relationships** - Ensure referenced IDs exist before creating records
3. **Enum values** must be UPPERCASE
4. **Date format** must be ISO 8601: `YYYY-MM-DDTHH:MM:SS`
5. **MRN must be unique** across all patients
6. **Source and destination hospitals** must be different for transfers