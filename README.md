# 🏥 MedCare System

A full-stack patient-hospital workflow optimization platform designed to reduce transfer errors between hospital systems and streamline medical record management.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.44-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Overview

MedCare System addresses critical inefficiencies in inter-hospital patient transfers by providing a unified platform for patient status tracking, real-time triage management, and secure medical record exchange. The system enables significant workflow improvements by consolidating patient intake, transfer coordination, and hospital capacity management under a single interface.

## ✨ Key Features

- **Patient Management**: Complete patient lifecycle tracking with medical records, triage levels, and admission history
- **Hospital Network**: Real-time hospital capacity monitoring and bed availability tracking
- **Transfer Workflow**: Streamlined patient transfer process with status updates and approval workflows
- **Triage System**: Dynamic triage level assignment and tracking (Critical, Urgent, Semi-Urgent, Non-Urgent)
- **Real-time Updates**: Live dashboard with instant data synchronization across all hospital systems
- **Audit Logging**: Complete audit trail for compliance and error tracking
- **RESTful API**: Well-documented API with interactive Swagger UI

## 🏗️ System Architecture

```
┌─────────────────┐
│   Frontend      │  HTML/CSS/JavaScript Dashboard
│   (Dashboard)   │  
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼────────┐
│   Backend API   │  FastAPI + Uvicorn
│   (FastAPI)     │  
└────────┬────────┘
         │
         │ ORM (SQLAlchemy)
         │
┌────────▼────────┐
│   Database      │  SQLite/PostgreSQL
│   (SQLAlchemy)  │  
└─────────────────┘
```

## 🚀 Technologies Used

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI web server implementation

### Frontend
- **HTML5/CSS3** - Modern responsive design
- **Vanilla JavaScript** - Client-side interactivity
- **Fetch API** - RESTful API communication

### Database
- **SQLite** - Development database (easily upgradeable to PostgreSQL)
- **Relationship Management** - Foreign keys and data integrity constraints

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Git

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/medcare-system.git
cd medcare-system
```

2. **Create virtual environment**
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the backend server**
```bash
python app.py
```

The server will start on `http://localhost:8000`

5. **Open the frontend**
- Navigate to the `frontend` folder
- Open `index.html` in your web browser
- Or use a live server extension in VS Code

## 📖 API Documentation

Once the server is running, access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Main Endpoints

#### Patients
- `GET /api/patients/` - List all patients
- `POST /api/patients/` - Create new patient
- `GET /api/patients/{id}` - Get patient by ID
- `PUT /api/patients/{id}/triage` - Update patient triage level
- `GET /api/patients/stats/triage-distribution` - Get triage statistics

#### Hospitals
- `GET /api/hospitals/` - List all hospitals
- `POST /api/hospitals/` - Create new hospital
- `GET /api/hospitals/{id}` - Get hospital by ID
- `GET /api/hospitals/{id}/patients` - Get all patients in hospital
- `PUT /api/hospitals/{id}/capacity` - Update bed availability
- `GET /api/hospitals/{id}/stats` - Get hospital statistics

#### Transfers
- `GET /api/transfers/` - List all transfers
- `POST /api/transfers/` - Create new transfer request
- `GET /api/transfers/{id}` - Get transfer by ID
- `PUT /api/transfers/{id}/status` - Update transfer status
- `GET /api/transfers/patient/{patient_id}` - Get patient transfer history

## 💾 Database Schema

### Patients Table
- Patient demographics and contact information
- Medical history and current medications
- Triage level and admission status
- Attending physician and diagnosis

### Hospitals Table
- Hospital information and location
- Capacity and bed availability
- Contact information

### Transfers Table
- Transfer requests and status tracking
- Source and destination hospitals
- Priority level and approval workflow
- Document transfer tracking

## 🔐 Data Models

### Triage Levels
- `CRITICAL` - Immediate attention required
- `URGENT` - Prompt attention needed
- `SEMI_URGENT` - Can wait for short period
- `NON_URGENT` - Stable condition

### Transfer Status
- `PENDING` - Awaiting approval
- `IN_PROGRESS` - Transfer initiated
- `COMPLETED` - Successfully transferred
- `CANCELLED` - Transfer cancelled

## 📊 Sample API Requests

### Create a Hospital
```json
POST /api/hospitals/
{
  "name": "San Jose Medical Center",
  "address": "123 Hospital Ave",
  "city": "San Jose",
  "state": "CA",
  "capacity": 150,
  "available_beds": 75
}
```

### Create a Patient
```json
POST /api/patients/
{
  "mrn": "MRN12345",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1985-05-15T00:00:00",
  "gender": "Male",
  "phone": "408-555-1234",
  "email": "john.doe@email.com",
  "blood_type": "O+",
  "hospital_id": 1,
  "triage_level": "URGENT"
}
```

### Create a Transfer
```json
POST /api/transfers/
{
  "patient_id": 1,
  "from_hospital_id": 1,
  "to_hospital_id": 2,
  "transfer_reason": "Requires specialized cardiac care",
  "priority": "URGENT",
  "requested_by": "Dr. Smith"
}
```

## 🎯 Key Achievements

- ✅ **Reduced Transfer Errors**: Unified system for secure record exchange
- ✅ **Optimized Workflows**: Streamlined patient intake and triage tracking
- ✅ **Real-time Monitoring**: Live dashboard for hospital capacity and patient status
- ✅ **Comprehensive Tracking**: Complete audit trail for compliance
- ✅ **Scalable Architecture**: Easily extensible to support multiple hospital networks

## 🛠️ Development

### Project Structure
```
medcare-system/
├── backend/
│   ├── app.py              # Main FastAPI application
│   ├── database.py         # Database configuration
│   ├── models.py           # SQLAlchemy models and Pydantic schemas
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── patients.py     # Patient endpoints
│   │   ├── hospitals.py    # Hospital endpoints
│   │   └── transfers.py    # Transfer endpoints
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Main dashboard
│   ├── styles.css          # Styling
│   └── app.js              # Frontend logic
└── README.md
```

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest
```

### Database Migration to PostgreSQL
To upgrade from SQLite to PostgreSQL:

1. Install PostgreSQL driver:
```bash
pip install psycopg2-binary
```

2. Update `DATABASE_URL` in `database.py`:
```python
DATABASE_URL = "postgresql://user:password@localhost/medcare_db"
```

## 🔮 Future Enhancements

- [ ] User authentication and role-based access control
- [ ] Email notifications for transfer approvals
- [ ] Advanced analytics dashboard with charts
- [ ] Mobile application (React Native)
- [ ] Integration with HL7/FHIR standards
- [ ] Telemedicine integration
- [ ] Automated bed assignment algorithms
- [ ] Predictive analytics for capacity planning

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Pradyumna (Sonu) Chirapu**
- Email: pradyumna.chirapu@gmail.com
- LinkedIn: [linkedin.com/in/your-profile](https://linkedin.com/in/your-profile)
- GitHub: [@yourusername](https://github.com/yourusername)

## 🙏 Acknowledgments

- FastAPI documentation and community
- SQLAlchemy ORM framework
- Healthcare IT best practices and standards

---

**Note**: This is a demonstration project for educational purposes. For production deployment in healthcare settings, additional security measures, HIPAA compliance, and proper data encryption must be implemented.