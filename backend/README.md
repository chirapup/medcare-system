# MedCare System - Backend API

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

Server will be available at `http://localhost:8000`

## API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

Create a `.env` file in the backend directory:

```
DATABASE_URL=sqlite:///./medcare.db
API_HOST=0.0.0.0
API_PORT=8000
```

## Database

The application uses SQLite by default. To use PostgreSQL:

1. Install PostgreSQL driver:
```bash
pip install psycopg2-binary
```

2. Update DATABASE_URL in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost/medcare_db
```

## Project Structure

```
backend/
├── app.py              # Main application entry point
├── database.py         # Database configuration
├── models.py           # Data models and schemas
├── routes/             # API route handlers
│   ├── patients.py
│   ├── hospitals.py
│   └── transfers.py
└── requirements.txt    # Python dependencies
```

## Adding New Routes

1. Create a new file in `routes/` directory
2. Define your router:
```python
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def get_items():
    return {"items": []}
```

3. Include it in `app.py`:
```python
from routes import your_new_route
app.include_router(your_new_route.router, prefix="/api/items", tags=["Items"])
```

## Testing

Use the interactive docs at `/docs` to test endpoints, or use curl:

```bash
# Health check
curl http://localhost:8000/health

# Get all hospitals
curl http://localhost:8000/api/hospitals/

# Create a hospital
curl -X POST http://localhost:8000/api/hospitals/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Hospital", "city": "San Jose", "state": "CA", "capacity": 100, "available_beds": 50}'
```