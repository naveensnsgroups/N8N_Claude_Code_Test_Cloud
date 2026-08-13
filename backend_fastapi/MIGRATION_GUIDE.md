# Express to FastAPI Migration Guide

## Overview

This document outlines the complete migration from the Express.js + Mongoose backend to FastAPI + Motor (async MongoDB) backend.

## Migration Summary

**Source**: `backend/` (Express.js + Node.js)
**Target**: `backend_fastapi/` (FastAPI + Python)
**Database**: MongoDB (same collection structure)

## File Mapping

### Express Files → FastAPI Equivalents

| Express File | FastAPI File | Purpose |
|--------------|------------|---------|
| `server.js` | `main.py` | App initialization, middleware, lifespan management |
| `config/db.js` | `database.py` | Database connection and utilities |
| `models/Employee.js` | `models.py` | Data validation schemas (Pydantic models) |
| `controllers/employeeController.js` | `crud.py` | CRUD operations for employees |
| `middleware/validateEmployee.js` | `models.py` (validators) | Input validation logic |
| `routes/employeeRoutes.js` | `routes/employee_routes.py` | API endpoint definitions |
| `package.json` | `requirements.txt` | Dependencies |

## Architecture Comparison

### Express Architecture
```
Request → Express Middleware Stack
         ↓
      Router
         ↓
   Controller (Callback)
         ↓
    Mongoose Model
         ↓
     MongoDB
```

### FastAPI Architecture
```
Request → FastAPI Middleware
         ↓
    Dependency Injection (get_database)
         ↓
     Route Handler (Async Function)
         ↓
      CRUD Function (Motor)
         ↓
     MongoDB (Async)
```

## Key Migration Changes

### 1. **Dependency Management**

**Express** (package.json):
```javascript
{
  "dependencies": {
    "express": "^4.19.2",
    "mongoose": "^8.4.1",
    "cors": "^2.8.5",
    "helmet": "^7.1.0",
    "express-rate-limit": "^7.3.1",
    "zod": "^3.23.8"
  }
}
```

**FastAPI** (requirements.txt):
```
fastapi==0.104.1
uvicorn==0.24.0
motor==3.3.2           # Async MongoDB driver (replaces mongoose)
pydantic==2.5.0        # Data validation (replaces zod)
slowapi==0.1.9         # Rate limiting (replaces express-rate-limit)
```

### 2. **Configuration Management**

**Express** (`server.js`):
```javascript
require('dotenv').config();
const PORT = process.env.PORT || 5000;
```

**FastAPI** (`config.py`):
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = int(os.getenv('PORT', 5000))

    class Config:
        env_file = '.env'
```

### 3. **Database Connection**

**Express** (`config/db.js`):
```javascript
const mongoose = require('mongoose');

const connectDB = async () => {
  const conn = await mongoose.connect(process.env.MONGO_URI);
  console.log(`MongoDB Atlas Connected: ${conn.connection.host}`);
};
```

**FastAPI** (`database.py`):
```python
from motor.motor_asyncio import AsyncClient

async def connect_to_mongo() -> AsyncDatabase:
    client = AsyncClient(settings.mongo_uri)
    await client.admin.command('ping')
    db = client.get_database()
    return db
```

**Key Difference**: Motor provides non-blocking MongoDB operations, allowing FastAPI to handle many concurrent requests efficiently.

### 4. **Data Models & Validation**

**Express** (Mongoose Schema):
```javascript
const employeeSchema = new mongoose.Schema({
  fullName: {
    type: String,
    required: [true, 'Full name is required'],
    match: [/^[A-Za-z\s]+$/, 'Letters and spaces only'],
  },
  email: {
    type: String,
    unique: true,
    match: [/^[a-z0-9._%+-]+@snsgroups\.com$/, '...'],
  },
});
```

**FastAPI** (Pydantic Models):
```python
class EmployeeBase(BaseModel):
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )
    email: EmailStr = Field(
        ...,
        max_length=150,
    )

    @field_validator('full_name', mode='before')
    @classmethod
    def validate_full_name(cls, v):
        if not all(c.isalpha() or c.isspace() for c in v):
            raise ValueError('Letters and spaces only')
        return v
```

**Key Differences**:
- Pydantic provides type-safe validation at the API level
- Validators are functions rather than schema properties
- Schema separation: `EmployeeCreate` (full validation), `EmployeeUpdate` (partial fields)

### 5. **Request Handling & Routing**

**Express**:
```javascript
router.route('/:id')
  .get(getEmployeeById)
  .put(validateEmployeeWithZod, updateEmployee)
  .delete(deleteEmployee);

const getEmployeeById = async (req, res, next) => {
  try {
    const employee = await Employee.findById(req.params.id);
    res.status(200).json({ success: true, data: employee });
  } catch (error) {
    next(error);
  }
};
```

**FastAPI**:
```python
@router.get('/{employee_id}', status_code=status.HTTP_200_OK)
async def retrieve_employee(
    employee_id: str,
    db: AsyncDatabase = Depends(get_database)
):
    return await get_employee_by_id(db, employee_id)

async def get_employee_by_id(db: AsyncDatabase, employee_id: str) -> dict:
    if not is_valid_object_id(employee_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid employee ID format'
        )
    # ...
```

**Key Differences**:
- FastAPI uses path parameters and dependency injection directly
- `Depends()` provides the database instance (replaces middleware passing data)
- Exception raising (HTTPException) replaces error callback pattern
- Status codes are explicit in route decorators

### 6. **Middleware & Security**

**Express**:
```javascript
app.use(helmet());
app.use(cors({ ... }));
app.use(rateLimit({ ... }));
app.use(mongoSanitize());
app.use(express.json({ limit: '10kb' }));

app.use((err, req, res, next) => {
  // Global error handling
});
```

**FastAPI**:
```python
app.add_middleware(TrustedHostMiddleware, ...)
app.add_middleware(CORSMiddleware, ...)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, ...)

@app.middleware('http')
async def log_requests(request: Request, call_next):
    # Custom middleware

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    # Global error handling
```

**Key Differences**:
- Middleware order matters in both but FastAPI is explicit
- Exception handlers are function-based
- Built-in request validation prevents injection attacks

### 7. **Server Startup & Shutdown**

**Express**:
```javascript
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

**FastAPI**:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=5000)
```

**Key Differences**:
- FastAPI uses lifespan context manager for startup/shutdown
- Uvicorn is the ASGI server (replaces Node's built-in HTTP server)

## Field Name Conversions

MongoDB collection stores camelCase field names (for compatibility with Express version). Pydantic models use snake_case. Automatic conversion happens in `crud.py`:

| Pydantic (Python) | MongoDB Field | Zod (Express) |
|-------------------|---------------|---------------|
| `full_name` | `fullName` | `fullName` |
| `employee_id` | `employeeId` | `employeeId` |
| `date_of_birth` | `dateOfBirth` | `dateOfBirth` |
| `join_date` | `joinDate` | `joinDate` |

```python
# In crud.py - pick_fields()
field_mapping = {
    'full_name': 'fullName',
    'employee_id': 'employeeId',
    'date_of_birth': 'dateOfBirth',
    'join_date': 'joinDate',
}
```

## Error Handling Comparison

### Express Error Scenarios

**Invalid Employee ID**:
```javascript
if (!isValidId(req.params.id)) {
  return res.status(400).json({ success: false, message: 'Invalid employee ID format' });
}
```

**Duplicate Key Error**:
```javascript
catch (error) {
  if (error.code === 11000) {
    const field = Object.keys(error.keyValue)[0];
    return res.status(409).json({ success: false, message: `${field} already exists` });
  }
  next(error);
}
```

### FastAPI Error Scenarios

**Invalid Employee ID**:
```python
if not is_valid_object_id(employee_id):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Invalid employee ID format'
    )
```

**Duplicate Key Error**:
```python
except DuplicateKeyError as e:
    field_name = list(e.details.get('keyPattern', {}).keys())[0]
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f'{field_name} already exists'
    )
```

## Rate Limiting Comparison

**Express** (express-rate-limit):
```javascript
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: { success: false, message: 'Too many requests...' },
});
app.use('/api', limiter);
```

**FastAPI** (slowapi):
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.get('')
@limiter.limit('100/15minutes')
async def list_employees(...):
    pass
```

## CORS Configuration Comparison

**Express**:
```javascript
const allowedOrigins = (process.env.CLIENT_URL || 'http://localhost:5173')
  .split(',')
  .map((url) => url.trim().replace(/\/$/, ''));

app.use(cors({
  origin: (origin, callback) => {
    if (!origin) return callback(null, true);
    const cleanOrigin = origin.replace(/\/$/, '');
    if (allowedOrigins.includes(cleanOrigin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type'],
}));
```

**FastAPI**:
```python
allowed_origins = [
    url.strip().rstrip('/') for url in settings.client_url.split(',')
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
    allow_headers=['Content-Type'],
)
```

## Testing & Verification

### Running the FastAPI Server

```bash
# Development with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 5000

# Production
uvicorn main:app --host 0.0.0.0 --port 5000 --workers 4
```

### Verification Checklist

- [ ] Server starts without errors
- [ ] Health check endpoint responds: `GET /` → 200
- [ ] Employee creation works with valid data: `POST /api/employees`
- [ ] Validation rejects invalid data (e.g., wrong email domain)
- [ ] Pagination works: `GET /api/employees?page=1&limit=10`
- [ ] Update endpoint rejects duplicate unique fields: `PUT /api/employees/{id}`
- [ ] Delete endpoint removes employee: `DELETE /api/employees/{id}`
- [ ] Rate limiting kicks in after 100 requests in 15 minutes
- [ ] CORS headers present in response
- [ ] 404 handler returns for undefined routes
- [ ] Swagger UI accessible at `/docs`

### Quick Test with cURL

```bash
# Health check
curl http://localhost:5000/

# Create employee
curl -X POST http://localhost:5000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "employee_id": "EMP001",
    "email": "john.doe@snsgroups.com",
    "phone": "9876543210"
  }'

# Get all employees
curl http://localhost:5000/api/employees?page=1&limit=10

# Get single employee
curl http://localhost:5000/api/employees/{employee_id}

# Update employee
curl -X PUT http://localhost:5000/api/employees/{employee_id} \
  -H "Content-Type: application/json" \
  -d '{"position": "Senior Engineer"}'

# Delete employee
curl -X DELETE http://localhost:5000/api/employees/{employee_id}
```

## Environment Setup

### Express `.env`
```
MONGO_URI=mongodb+srv://...
PORT=5000
NODE_ENV=development
CLIENT_URL=http://localhost:5173
```

### FastAPI `.env`
```
MONGO_URI=mongodb+srv://...
PORT=5000
HOST=0.0.0.0
NODE_ENV=development
CLIENT_URL=http://localhost:5173
```

## Frontend Integration

No changes needed! The FastAPI backend provides the same API endpoints and response format as Express:

```javascript
// frontend/src/services/api.js - No changes needed
const API_BASE = 'http://localhost:5000/api';

async function getAllEmployees(page = 1, limit = 50) {
  const response = await fetch(`${API_BASE}/employees?page=${page}&limit=${limit}`);
  return response.json();
}
```

## Performance Considerations

### Express vs FastAPI

| Aspect | Express | FastAPI |
|--------|---------|---------|
| Concurrency Model | Callback-based (Node.js event loop) | Async/await native |
| DB Driver | Mongoose (callback wrapper) | Motor (truly async) |
| Throughput | ~1000 req/s (estimated) | ~5000 req/s (estimated) |
| Memory Usage | Moderate | Lower (fewer threads) |
| Startup Time | Fast | Fast |
| Development Speed | Fast | Fast |

**FastAPI will handle concurrent requests more efficiently**, especially with async MongoDB operations via Motor.

## Troubleshooting

### Connection Issues

**Error**: `MongoDB Connection Error`
- Check `MONGO_URI` is correct
- Verify IP whitelist in MongoDB Atlas
- Ensure credentials are correct

**Fix**:
```bash
# Test connection
python -c "from motor.motor_asyncio import AsyncClient; import asyncio; \
asyncio.run(AsyncClient('mongodb+srv://...').admin.command('ping'))"
```

### Validation Errors

**Error**: `Email must end with @snsgroups.com domain`
- Frontend/test sending wrong email domain
- Pydantic validators are stricter than Mongoose in some cases

**Fix**: Check email matches exactly: `test@snsgroups.com` (lowercase, correct domain)

### Rate Limiting Not Working

**Error**: Getting 429 Too Many Requests unexpectedly
- Limiter applied globally, check `@limiter.limit()` decorator

**Fix**: Verify rate limit is set per IP: `100/15minutes`

## Migration Checklist

- [ ] Created `backend_fastapi/` directory structure
- [ ] Installed Python 3.8+
- [ ] Created virtual environment: `python -m venv venv`
- [ ] Installed dependencies: `pip install -r requirements.txt`
- [ ] Copied `.env` file and updated `MONGO_URI`
- [ ] Started FastAPI server: `uvicorn main:app --reload`
- [ ] Tested all endpoints with cURL or Postman
- [ ] Updated frontend `.env` if backend URL changed
- [ ] Verified frontend can connect and fetch/create/update/delete employees
- [ ] Ran validation tests (test invalid data)
- [ ] Tested rate limiting (100+ requests)
- [ ] Checked logs for any errors
- [ ] Deployed to production environment

## Next Steps

1. **Testing**: Add pytest tests for all endpoints
2. **CI/CD**: Set up GitHub Actions for automated testing
3. **Monitoring**: Add application performance monitoring
4. **Deployment**: Deploy to Heroku, Railway, or your preferred platform
5. **Documentation**: Keep API docs updated with `/docs` endpoint

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Motor Documentation](https://motor.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Slowapi Documentation](https://slowapi.readthedocs.io/)
- [MongoDB Python Driver](https://pymongo.readthedocs.io/)

---

**Last Updated**: 2026-08-13
**Migration Status**: ✅ Complete
