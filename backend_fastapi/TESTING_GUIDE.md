# Testing Guide - FastAPI Backend

## Manual Testing with cURL

### Setup

Start the server first:
```bash
cd backend_fastapi
uvicorn main:app --reload
```

Server should show:
```
INFO:     Application startup complete
```

### Test Cases

#### 1. Health Check
```bash
curl -X GET http://localhost:5000/
```

**Expected Response (200)**:
```json
{"success": true, "message": "Personal Details API is running."}
```

---

#### 2. Create Employee - Valid Data

```bash
curl -X POST http://localhost:5000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "employee_id": "EMP001",
    "email": "john.doe@snsgroups.com",
    "phone": "9876543210"
  }'
```

**Expected Response (201)**:
```json
{
  "success": true,
  "message": "Employee created successfully",
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "fullName": "John Doe",
    "employeeId": "EMP001",
    "email": "john.doe@snsgroups.com",
    "phone": "9876543210",
    "createdAt": "2024-01-15T10:30:00",
    "updatedAt": "2024-01-15T10:30:00"
  }
}
```

**Save the `_id` for next tests.**

---

#### 3. Create Employee - Full Data with Optional Fields

```bash
curl -X POST http://localhost:5000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Smith",
    "employee_id": "EMP002",
    "email": "jane.smith@snsgroups.com",
    "phone": "8765432109",
    "date_of_birth": "1990-05-20T00:00:00",
    "gender": "Female",
    "address": "456 Oak Ave, Springfield",
    "department": "Finance",
    "position": "Financial Analyst",
    "join_date": "2022-03-15T00:00:00"
  }'
```

**Expected Response (201)**: Same as above with all fields included.

---

#### 4. Validation - Missing Required Field (email)

```bash
curl -X POST http://localhost:5000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Bob Johnson",
    "employee_id": "EMP003",
    "phone": "5555555555"
  }'
```

**Expected Response (422)**:
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "email"],
      "msg": "Field required",
      "input": { ... }
    }
  ]
}
```

---

#### 5. Validation - Invalid Email Domain

```bash
curl -X POST http://localhost:5000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Bob Johnson",
    "employee_id": "EMP003",
    "email": "bob@gmail.com",
    "phone": "5555555555"
  }'
```

**Expected Response (422)**:
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "Email must end with @snsgroups.com domain",
      "input": "bob@gmail.com"
    }
  ]
}
```

---

#### 6. Validation - Invalid Full Name (with numbers)

```bash
curl -X POST http://localhost:5000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe 123",
    "employee_id": "EMP004",
    "email": "john123@snsgroups.com",
    "phone": "5555555555"
  }'
```

**Expected Response (422)**:
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "full_name"],
      "msg": "Full name must contain only letters and spaces",
      "input": "John Doe 123"
    }
  ]
}
```

---

#### 7. Validation - Invalid Employee ID (wrong format)

```bash
curl -X POST http://localhost:5000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Bob Johnson",
    "employee_id": "BOB001",
    "email": "bob@snsgroups.com",
    "phone": "5555555555"
  }'
```

**Expected Response (422)**:
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "employee_id"],
      "msg": "Employee ID must start with EMP followed by numbers",
      "input": "BOB001"
    }
  ]
}
```

---

#### 8. Validation - Invalid Phone (wrong length)

```bash
curl -X POST http://localhost:5000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Bob Johnson",
    "employee_id": "EMP005",
    "email": "bob@snsgroups.com",
    "phone": "55555"
  }'
```

**Expected Response (422)**:
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "phone"],
      "msg": "Phone number must be exactly 10 digits",
      "input": "55555"
    }
  ]
}
```

---

#### 9. Get All Employees - Default Pagination

```bash
curl http://localhost:5000/api/employees
```

**Expected Response (200)**:
```json
{
  "success": true,
  "count": 2,
  "total": 2,
  "page": 1,
  "pages": 1,
  "data": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "fullName": "Jane Smith",
      "employeeId": "EMP002",
      ...
    },
    {
      "_id": "507f1f77bcf86cd799439012",
      "fullName": "John Doe",
      "employeeId": "EMP001",
      ...
    }
  ]
}
```

**Note**: Sorted by `createdAt` descending (newest first).

---

#### 10. Get All Employees - With Pagination

```bash
# Get page 1, 1 record per page
curl "http://localhost:5000/api/employees?page=1&limit=1"
```

**Expected Response (200)**:
```json
{
  "success": true,
  "count": 1,
  "total": 2,
  "page": 1,
  "pages": 2,
  "data": [ ... ]
}
```

```bash
# Get page 2
curl "http://localhost:5000/api/employees?page=2&limit=1"
```

---

#### 11. Get Single Employee by ID

```bash
# Replace with actual ID from creation response
curl http://localhost:5000/api/employees/507f1f77bcf86cd799439011
```

**Expected Response (200)**:
```json
{
  "success": true,
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "fullName": "John Doe",
    "employeeId": "EMP001",
    ...
  }
}
```

---

#### 12. Get Employee - Invalid ID Format

```bash
curl http://localhost:5000/api/employees/invalid_id
```

**Expected Response (400)**:
```json
{
  "detail": "Invalid employee ID format"
}
```

---

#### 13. Get Employee - Non-existent ID

```bash
# Valid MongoDB ObjectId format but doesn't exist
curl http://localhost:5000/api/employees/507f1f77bcf86cd799439999
```

**Expected Response (404)**:
```json
{
  "detail": "Employee not found"
}
```

---

#### 14. Update Employee - Partial Update

```bash
curl -X PUT http://localhost:5000/api/employees/507f1f77bcf86cd799439011 \
  -H "Content-Type: application/json" \
  -d '{
    "position": "Senior Software Engineer",
    "department": "IT"
  }'
```

**Expected Response (200)**:
```json
{
  "success": true,
  "message": "Employee updated successfully",
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "fullName": "John Doe",
    "employeeId": "EMP001",
    "email": "john.doe@snsgroups.com",
    "phone": "9876543210",
    "position": "Senior Software Engineer",
    "department": "IT",
    ...
  }
}
```

---

#### 15. Update Employee - Duplicate Unique Field

```bash
curl -X PUT http://localhost:5000/api/employees/507f1f77bcf86cd799439011 \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane.smith@snsgroups.com"
  }'
```

**Expected Response (409)**:
```json
{
  "detail": "email already exists"
}
```

---

#### 16. Update Employee - Validation on Update

```bash
curl -X PUT http://localhost:5000/api/employees/507f1f77bcf86cd799439011 \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe 123"
  }'
```

**Expected Response (422)**:
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "full_name"],
      "msg": "Full name must contain only letters and spaces"
    }
  ]
}
```

---

#### 17. Delete Employee

```bash
curl -X DELETE http://localhost:5000/api/employees/507f1f77bcf86cd799439011
```

**Expected Response (200)**:
```json
{
  "success": true,
  "message": "Employee deleted successfully"
}
```

---

#### 18. Delete Employee - Already Deleted

```bash
curl -X DELETE http://localhost:5000/api/employees/507f1f77bcf86cd799439011
```

**Expected Response (404)**:
```json
{
  "detail": "Employee not found"
}
```

---

#### 19. 404 - Undefined Route

```bash
curl http://localhost:5000/api/undefined
```

**Expected Response (404)**:
```json
{
  "success": false,
  "message": "Route not found"
}
```

---

#### 20. Rate Limiting (100 requests per 15 minutes)

```bash
# Make 101 requests quickly
for i in {1..101}; do
  curl http://localhost:5000/
done
```

**Request 101 Response (429)**:
```json
{
  "success": false,
  "message": "Too many requests, please try again later."
}
```

---

## Automated Testing with pytest

### Setup

```bash
pip install pytest pytest-asyncio httpx
```

### Create `test_main.py`

```python
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json()["success"] is True

@pytest.mark.asyncio
async def test_create_employee_valid():
    async with AsyncClient(app=app, base_url="http://test") as client:
        employee_data = {
            "full_name": "Test User",
            "employee_id": "EMP999",
            "email": "test@snsgroups.com",
            "phone": "1234567890",
        }
        response = await client.post("/api/employees", json=employee_data)
        assert response.status_code == 201
        assert response.json()["success"] is True

@pytest.mark.asyncio
async def test_create_employee_invalid_email():
    async with AsyncClient(app=app, base_url="http://test") as client:
        employee_data = {
            "full_name": "Test User",
            "employee_id": "EMP998",
            "email": "test@gmail.com",
            "phone": "1234567890",
        }
        response = await client.post("/api/employees", json=employee_data)
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_list_employees():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/employees")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "page" in data
        assert "total" in data
```

### Run Tests

```bash
pytest test_main.py -v

# With coverage
pip install pytest-cov
pytest test_main.py --cov=. --cov-report=html
```

---

## Integration Testing - Full Flow

```bash
# 1. Create employee
EMPLOYEE_ID=$(curl -s -X POST http://localhost:5000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "employee_id": "EMP100",
    "email": "test@snsgroups.com",
    "phone": "1234567890"
  }' | jq -r '.data._id')

echo "Created employee: $EMPLOYEE_ID"

# 2. Get the employee
curl http://localhost:5000/api/employees/$EMPLOYEE_ID

# 3. Update the employee
curl -X PUT http://localhost:5000/api/employees/$EMPLOYEE_ID \
  -H "Content-Type: application/json" \
  -d '{"position": "Engineer"}'

# 4. List employees
curl http://localhost:5000/api/employees

# 5. Delete the employee
curl -X DELETE http://localhost:5000/api/employees/$EMPLOYEE_ID
```

---

## Postman Collection

Import this JSON into Postman:

```json
{
  "info": {
    "name": "Employee API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/"
      }
    },
    {
      "name": "Create Employee",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/api/employees",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"full_name\": \"John Doe\",\n  \"employee_id\": \"EMP001\",\n  \"email\": \"john.doe@snsgroups.com\",\n  \"phone\": \"9876543210\"\n}"
        }
      }
    },
    {
      "name": "Get All Employees",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/employees?page=1&limit=50"
      }
    },
    {
      "name": "Get Employee by ID",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/employees/{{employee_id}}"
      }
    },
    {
      "name": "Update Employee",
      "request": {
        "method": "PUT",
        "url": "{{base_url}}/api/employees/{{employee_id}}",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"position\": \"Senior Engineer\"\n}"
        }
      }
    },
    {
      "name": "Delete Employee",
      "request": {
        "method": "DELETE",
        "url": "{{base_url}}/api/employees/{{employee_id}}"
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:5000"
    },
    {
      "key": "employee_id",
      "value": ""
    }
  ]
}
```

Set `{{base_url}}` to `http://localhost:5000` and `{{employee_id}}` with actual MongoDB ObjectId.

---

## Load Testing

### Using Apache Bench

```bash
# Simple load test - 1000 requests, 10 concurrent
ab -n 1000 -c 10 http://localhost:5000/

# Health check load test
ab -n 1000 -c 50 http://localhost:5000/
```

### Using wrk

```bash
# 4 threads, 100 connections, 30 second duration
wrk -t4 -c100 -d30s http://localhost:5000/

# GET with custom script
wrk -t4 -c100 -d30s -s script.lua http://localhost:5000/api/employees
```

---

## Debugging

### Enable Debug Logging

```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Use FastAPI Debug Mode

```python
app = FastAPI(debug=True)
```

### Check Server Health

```bash
# Check if server is running
curl -v http://localhost:5000/

# Check MongoDB connection in server logs
# Look for: "MongoDB Atlas Connected successfully"
```

### Test Individual Components

```python
# Test Pydantic validation
from models import EmployeeCreate

try:
    emp = EmployeeCreate(
        full_name="John",
        employee_id="INVALID",
        email="test@snsgroups.com",
        phone="1234567890"
    )
except ValueError as e:
    print(f"Validation error: {e}")

# Test database connection
from database import connect_to_mongo, get_database
import asyncio

async def test_db():
    db = await connect_to_mongo()
    result = await db.admin.command('ping')
    print(f"Ping result: {result}")

asyncio.run(test_db())
```

---

## Common Test Scenarios Checklist

- [ ] Create employee with all required fields
- [ ] Create employee with optional fields
- [ ] Verify created employee appears in list
- [ ] Pagination works correctly
- [ ] Sorting by createdAt (descending)
- [ ] Can fetch single employee by ID
- [ ] Cannot fetch with invalid ID format
- [ ] Cannot fetch non-existent ID
- [ ] Can update partial fields
- [ ] Cannot update with invalid data
- [ ] Cannot create duplicate email
- [ ] Cannot create duplicate employee_id
- [ ] Can delete employee
- [ ] Cannot delete already deleted employee
- [ ] Rate limiting blocks after 100 requests
- [ ] CORS headers present
- [ ] 404 for undefined routes
- [ ] API documentation at /docs
- [ ] Email automatically converted to lowercase
- [ ] String fields trimmed
- [ ] Enum validation (gender, department)

---

## Performance Benchmarks

Expected response times:
- GET / (health): < 10ms
- POST /api/employees (create): < 50ms
- GET /api/employees (list): < 100ms
- GET /api/employees/{id}: < 50ms
- PUT /api/employees/{id}: < 75ms
- DELETE /api/employees/{id}: < 50ms

Expected throughput:
- ~5000 req/s on modern hardware with 4 workers
- Can handle 100+ concurrent connections
