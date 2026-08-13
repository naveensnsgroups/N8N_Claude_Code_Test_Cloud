# FastAPI Backend - Quick Start Guide

## Installation (5 minutes)

### 1. Install Python dependencies
```bash
cd backend_fastapi

# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your MongoDB URI
# MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/dbname?retryWrites=true&w=majority
```

### 3. Start the server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

You should see:
```
INFO:     Application startup complete
INFO:     Server running in development mode on port 5000
INFO:     Uvicorn running on http://0.0.0.0:5000
```

## Test the API

### Health Check
```bash
curl http://localhost:5000/
```

Expected response:
```json
{"success": true, "message": "Personal Details API is running."}
```

### Create an Employee
```bash
curl -X POST http://localhost:5000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "employee_id": "EMP001",
    "email": "john.doe@snsgroups.com",
    "phone": "9876543210",
    "department": "IT",
    "position": "Software Engineer"
  }'
```

### Get All Employees
```bash
curl http://localhost:5000/api/employees?page=1&limit=10
```

### Get Single Employee
```bash
# Replace {id} with actual MongoDB ObjectId from creation response
curl http://localhost:5000/api/employees/{id}
```

### Update Employee
```bash
curl -X PUT http://localhost:5000/api/employees/{id} \
  -H "Content-Type: application/json" \
  -d '{"position": "Senior Engineer"}'
```

### Delete Employee
```bash
curl -X DELETE http://localhost:5000/api/employees/{id}
```

## Interactive API Documentation

Visit `http://localhost:5000/docs` in your browser to:
- See all API endpoints
- View request/response schemas
- Test endpoints directly
- View validation rules

## Common Issues

### Port 5000 already in use
```bash
# Use a different port
uvicorn main:app --reload --port 5001
```

### MongoDB connection fails
```
ERROR: MongoDB Connection Error: [Errno -2] Name or service not known
```

- Check `MONGO_URI` in `.env` is correct
- Verify IP is whitelisted in MongoDB Atlas
- Check internet connection

### Validation error on email
```
Email must end with @snsgroups.com domain
```

- Use emails ending with exactly `@snsgroups.com` (lowercase)
- Not `@SnsGroups.com` or other variations

### Phone validation fails
```
Phone number must be exactly 10 digits
```

- Phone must be exactly 10 numeric characters
- No hyphens, spaces, or country codes
- Example: `9876543210` ✅ vs `+1 987 654 3210` ❌

## Production Deployment

### Using Uvicorn with multiple workers
```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --workers 4
```

### Using Gunicorn with Uvicorn workers
```bash
pip install gunicorn

gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:5000
```

### Environment variables
```bash
export NODE_ENV=production
export MONGO_URI=<your-atlas-uri>
export PORT=5000
export CLIENT_URL=https://yourdomain.com
```

## File Structure

```
backend_fastapi/
├── main.py                 # FastAPI app setup
├── config.py              # Configuration
├── database.py            # MongoDB connection
├── models.py              # Pydantic schemas
├── crud.py                # Database operations
├── routes/
│   └── employee_routes.py # API endpoints
├── requirements.txt       # Dependencies
├── .env.example          # Example config
├── .gitignore            # Git ignore rules
├── README.md             # Full documentation
└── QUICKSTART.md         # This file
```

## Next Steps

1. **Explore the code**: Start with `main.py` to understand the structure
2. **Read the README**: For detailed API documentation
3. **Review MIGRATION_GUIDE.md**: For differences from Express
4. **Integrate with frontend**: Update frontend API calls if needed
5. **Add tests**: Create test files with pytest

## Useful Commands

```bash
# Format code with Black
pip install black
black .

# Type checking with mypy
pip install mypy
mypy .

# Linting with flake8
pip install flake8
flake8 .

# Run in production mode (no reload)
uvicorn main:app --host 0.0.0.0 --port 5000

# View server logs
tail -f logs/app.log
```

## Stopping the Server

Press `Ctrl+C` in the terminal where uvicorn is running.

## Need Help?

- Read the full `README.md` in this directory
- Check `MIGRATION_GUIDE.md` for Express → FastAPI mappings
- Visit [FastAPI Docs](https://fastapi.tiangolo.com/)
- Check [Motor Documentation](https://motor.readthedocs.io/)
