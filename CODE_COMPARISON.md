# Code Comparison: Express vs FastAPI

This document provides side-by-side comparisons of key code sections from the Express backend and their FastAPI equivalents.

## Table of Contents
1. [Server Setup](#server-setup)
2. [Database Connection](#database-connection)
3. [Models/Schemas](#modelsschemas)
4. [CRUD Operations](#crud-operations)
5. [Routes/Endpoints](#routesendpoints)
6. [Middleware](#middleware)
7. [Error Handling](#error-handling)

---

## Server Setup

### Express (`server.js`)
```javascript
const express    = require('express');
const cors       = require('cors');
const helmet     = require('helmet');
const rateLimit  = require('express-rate-limit');
const dotenv     = require('dotenv');

dotenv.config();

const app = express();

// Security Middleware
app.use(helmet());
app.use(cors({ ... }));

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
});
app.use('/api', limiter);

app.use(express.json({ limit: '10kb' }));

app.use('/api/employees', require('./routes/employeeRoutes'));

app.get('/', (req, res) => {
  res.json({ success: true, message: 'Personal Details API is running.' });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

### FastAPI (`main.py`)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from contextlib import asynccontextmanager

from config import get_settings
from database import connect_to_mongo, close_mongo_connection
from routes import employee_routes

settings = get_settings()
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[...],
    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
    allow_headers=['Content-Type'],
)

app.include_router(
    employee_routes.router,
    prefix='/api/employees',
    tags=['employees']
)

@app.get('/')
async def health_check():
    return {'success': True, 'message': 'Personal Details API is running.'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host=settings.host, port=settings.port)
```

### Key Differences
| Aspect | Express | FastAPI |
|--------|---------|---------|
| **Sync/Async** | Callback-based | Native async/await |
| **Server** | Built-in HTTP server | Uvicorn (ASGI) |
| **Body Limit** | Explicit (10kb) | Default (25MB) |
| **Startup/Shutdown** | Direct calls | Context manager (lifespan) |
| **Route Mounting** | `app.use()` | `app.include_router()` |

---

## Database Connection

### Express (`config/db.js`)
```javascript
const mongoose = require('mongoose');

const connectDB = async () => {
  if (!process.env.MONGO_URI) {
    console.error('MONGO_URI is not defined');
    process.exit(1);
  }

  try {
    const conn = await mongoose.connect(process.env.MONGO_URI);
    console.log(`MongoDB Atlas Connected: ${conn.connection.host}`);
  } catch (error) {
    console.error(`MongoDB Connection Error: ${error.message}`);
    process.exit(1);
  }
};

module.exports = connectDB;
```

### FastAPI (`database.py`)
```python
from motor.motor_asyncio import AsyncClient, AsyncDatabase

async def connect_to_mongo() -> AsyncDatabase:
    """Establish connection to MongoDB Atlas."""
    settings = get_settings()

    if not settings.mongo_uri:
        logger.error('MONGO_URI is not defined')
        raise ValueError('MONGO_URI is not defined')

    try:
        client = AsyncClient(settings.mongo_uri)
        await client.admin.command('ping')
        db = client.get_database()
        logger.info('MongoDB Atlas Connected successfully')
        return db
    except Exception as error:
        logger.error(f'MongoDB Connection Error: {str(error)}')
        raise

async def close_mongo_connection() -> None:
    """Close the MongoDB connection."""
    if db is not None:
        db.client.close()
        logger.info('MongoDB connection closed')
```

### Key Differences
| Aspect | Express | FastAPI |
|--------|---------|---------|
| **Driver** | Mongoose (abstraction) | Motor (native async) |
| **Connection Pool** | Auto-managed by Mongoose | Auto-managed by Motor |
| **Error Handling** | `process.exit()` | Exception raising |
| **Ping Command** | Not explicit | Explicit ping test |
| **Cleanup** | Implicit | Explicit in lifespan |

---

## Models/Schemas

### Express (Mongoose Schema - `models/Employee.js`)
```javascript
const employeeSchema = new mongoose.Schema(
  {
    fullName: {
      type: String,
      required: [true, 'Full name is required'],
      trim: true,
      maxlength: [100, '...'],
      match: [/^[A-Za-z\s]+$/, '...'],
    },
    employeeId: {
      type: String,
      required: [true, 'Employee ID is required'],
      unique: true,
      trim: true,
      match: [/^EMP\d+$/, '...'],
    },
    email: {
      type: String,
      required: [true, 'Email is required'],
      unique: true,
      lowercase: true,
      trim: true,
      match: [/^[a-z0-9._%+-]+@snsgroups\.com$/, '...'],
    },
    phone: {
      type: String,
      required: [true, 'Phone number is required'],
      trim: true,
      match: [/^\d{10}$/, '...'],
    },
    gender: {
      type: String,
      enum: {
        values: ['Male', 'Female', 'Other'],
        message: '{VALUE} is not valid',
      },
    },
  },
  { timestamps: true }
);

module.exports = mongoose.model('Employee', employeeSchema, 'HR');
```

### FastAPI (Pydantic Models - `models.py`)
```python
from pydantic import BaseModel, Field, EmailStr, field_validator
from enum import Enum

class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class EmployeeBase(BaseModel):
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Employee full name"
    )
    employee_id: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Unique employee ID"
    )
    email: EmailStr = Field(
        ...,
        max_length=150,
        description="Email address"
    )
    phone: str = Field(
        ...,
        min_length=10,
        max_length=10,
        description="Phone number"
    )
    gender: Optional[GenderEnum] = None

    @field_validator('full_name', mode='before')
    @classmethod
    def validate_full_name(cls, v):
        if v and not all(c.isalpha() or c.isspace() for c in v):
            raise ValueError('Letters and spaces only')
        return v

    @field_validator('email', mode='before')
    @classmethod
    def validate_email_domain(cls, v):
        if v and not v.lower().endswith('@snsgroups.com'):
            raise ValueError('Email must end with @snsgroups.com')
        return v

class EmployeeCreate(EmployeeBase):
    """Schema for creating employees."""
    pass

class EmployeeUpdate(BaseModel):
    """Schema for updating employees (all fields optional)."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    # ... other optional fields
```

### Key Differences
| Aspect | Express | FastAPI |
|--------|---------|---------|
| **Validation Location** | Schema definition | Validator functions |
| **Type Safety** | Runtime via Mongoose | Static (Pydantic + mypy) |
| **Uniqueness** | `unique: true` in schema | DB index constraint |
| **Timestamps** | Automatic `timestamps: true` | Manual in response model |
| **Create vs Update** | Single schema | Separate schemas |
| **Documentation** | Implicit | Explicit via Field() |

---

## CRUD Operations

### Express Get All (`controllers/employeeController.js`)
```javascript
const getAllEmployees = async (req, res, next) => {
  try {
    const page  = Math.max(1, parseInt(req.query.page)  || 1);
    const limit = Math.min(100, parseInt(req.query.limit) || 50);
    const skip  = (page - 1) * limit;

    const [employees, total] = await Promise.all([
      Employee.find().sort({ createdAt: -1 }).skip(skip).limit(limit),
      Employee.countDocuments(),
    ]);

    res.status(200).json({
      success: true,
      count: employees.length,
      total,
      page,
      pages: Math.ceil(total / limit),
      data: employees,
    });
  } catch (error) {
    next(error);
  }
};
```

### FastAPI Get All (`crud.py`)
```python
async def get_all_employees(
    db: AsyncDatabase,
    page: int = 1,
    limit: int = 50
) -> dict:
    page = max(1, page)
    limit = min(100, limit)
    skip = (page - 1) * limit

    collection = db[COLLECTION_NAME]

    employees = await collection.find() \
        .sort('createdAt', -1) \
        .skip(skip) \
        .limit(limit) \
        .to_list(length=limit)

    total = await collection.count_documents({})

    for emp in employees:
        emp['_id'] = str(emp['_id'])

    return {
        'success': True,
        'count': len(employees),
        'total': total,
        'page': page,
        'pages': (total + limit - 1) // limit,
        'data': employees,
    }
```

### Express Create (`controllers/employeeController.js`)
```javascript
const createEmployee = async (req, res, next) => {
  try {
    const safeData = pickFields(req.body);
    const employee = await Employee.create(safeData);
    res.status(201).json({
      success: true,
      message: 'Employee created successfully',
      data: employee,
    });
  } catch (error) {
    if (error.code === 11000) {
      const field = Object.keys(error.keyValue)[0];
      return res.status(409).json({
        success: false,
        message: `${field} already exists`,
      });
    }
    next(error);
  }
};
```

### FastAPI Create (`crud.py`)
```python
async def create_employee(
    db: AsyncDatabase,
    employee_data: EmployeeCreate
) -> dict:
    collection = db[COLLECTION_NAME]
    data_dict = employee_data.model_dump(exclude_unset=True)
    safe_data = pick_fields(data_dict)

    try:
        result = await collection.insert_one(safe_data)
        created_employee = await collection.find_one({'_id': result.inserted_id})
        created_employee['_id'] = str(created_employee['_id'])

        return {
            'success': True,
            'message': 'Employee created successfully',
            'data': created_employee,
        }
    except DuplicateKeyError as e:
        field_name = list(e.details.get('keyPattern', {}).keys())[0]
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'{field_name} already exists',
        )
```

### Key Differences
| Aspect | Express | FastAPI |
|--------|---------|---------|
| **Error Handling** | `next(error)` callback | `raise HTTPException()` |
| **DB Method** | `Model.create()` | `collection.insert_one()` |
| **Duplicate Errors** | Check `error.code === 11000` | Catch `DuplicateKeyError` |
| **Response Format** | `res.json()` | Return dict (auto JSON) |
| **Validation** | Mongoose schema + Zod middleware | Pydantic model |
| **Field Conversion** | Post-validation in pickFields | Pre-save in pick_fields |

---

## Routes/Endpoints

### Express Routes (`routes/employeeRoutes.js`)
```javascript
const express = require('express');
const router = express.Router();
const validateEmployeeWithZod = require('../middleware/validateEmployee');
const {
  getAllEmployees,
  getEmployeeById,
  createEmployee,
  updateEmployee,
  deleteEmployee,
} = require('../controllers/employeeController');

router
  .route('/')
  .get(getAllEmployees)
  .post(validateEmployeeWithZod, createEmployee);

router
  .route('/:id')
  .get(getEmployeeById)
  .put(validateEmployeeWithZod, updateEmployee)
  .delete(deleteEmployee);

module.exports = router;
```

### FastAPI Routes (`routes/employee_routes.py`)
```python
from fastapi import APIRouter, Depends, Query, status

router = APIRouter()

@router.get(
    '',
    response_model=PaginatedEmployeeResponse,
    status_code=status.HTTP_200_OK,
)
async def list_employees(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncDatabase = Depends(get_database)
):
    return await get_all_employees(db, page, limit)

@router.get('/{employee_id}', status_code=status.HTTP_200_OK)
async def retrieve_employee(
    employee_id: str,
    db: AsyncDatabase = Depends(get_database)
):
    return await get_employee_by_id(db, employee_id)

@router.post('', status_code=status.HTTP_201_CREATED)
async def create_new_employee(
    employee_data: EmployeeCreate,
    db: AsyncDatabase = Depends(get_database)
):
    return await create_employee(db, employee_data)

@router.put('/{employee_id}', status_code=status.HTTP_200_OK)
async def update_existing_employee(
    employee_id: str,
    employee_data: EmployeeUpdate,
    db: AsyncDatabase = Depends(get_database)
):
    return await update_employee(db, employee_id, employee_data)

@router.delete('/{employee_id}', status_code=status.HTTP_200_OK)
async def delete_existing_employee(
    employee_id: str,
    db: AsyncDatabase = Depends(get_database)
):
    return await delete_employee(db, employee_id)
```

### Key Differences
| Aspect | Express | FastAPI |
|--------|---------|---------|
| **Routing Style** | Chainable `.route()` | Decorator-based |
| **Validation** | Middleware in chain | Parameter in function |
| **DB Access** | Implicit (global Model) | Dependency injection |
| **Path Parameters** | `:id` syntax | `{id}` syntax |
| **Query Validation** | Manual parseInt | Automatic via Query() |
| **Status Codes** | No type safety | Explicit status_code |
| **Documentation** | None automatic | Auto-generated |

---

## Middleware

### Express CORS & Rate Limiting
```javascript
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

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: { success: false, message: 'Too many requests...' },
});
app.use('/api', limiter);

app.use((err, req, res, next) => {
  console.error(`[ERROR] ${req.method} ${req.originalUrl} —`, err.message);
  if (err.name === 'ValidationError') {
    const messages = Object.values(err.errors).map((e) => e.message);
    return res.status(400).json({ success: false, message: messages.join(', ') });
  }
  res.status(err.statusCode || 500).json({ success: false, message: err.message });
});
```

### FastAPI CORS & Rate Limiting
```python
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
    allow_headers=['Content-Type'],
)

limiter = Limiter(key_func=get_remote_address)

@router.get('')
@limiter.limit('100/15minutes')
async def list_employees(...):
    pass

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f'[ERROR] {request.method} {request.url.path} — {str(exc)}')
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'success': False, 'message': str(exc)}
    )
```

### Key Differences
| Aspect | Express | FastAPI |
|--------|---------|---------|
| **CORS Style** | Dynamic callback | List of origins |
| **Rate Limit Scope** | Global per path | Per route decorator |
| **Error Handling** | 4-parameter middleware | Exception handler |
| **Middleware Order** | Sequential add | First in, last executed |

---

## Error Handling

### Express Error Handling
```javascript
// Validation
if (!isValidId(req.params.id)) {
  return res.status(400).json({
    success: false,
    message: 'Invalid employee ID format'
  });
}

// Not Found
if (!employee) {
  return res.status(404).json({
    success: false,
    message: 'Employee not found'
  });
}

// Duplicate Key
if (error.code === 11000) {
  const field = Object.keys(error.keyValue)[0];
  return res.status(409).json({
    success: false,
    message: `${field} already exists`
  });
}

// Global Error Handler
app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  res.status(statusCode).json({
    success: false,
    message: process.env.NODE_ENV === 'production'
      ? 'Internal Server Error'
      : err.message
  });
});
```

### FastAPI Error Handling
```python
# Validation (automatic via Pydantic)
if not is_valid_object_id(employee_id):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Invalid employee ID format'
    )

# Not Found
if not employee:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Employee not found'
    )

# Duplicate Key
try:
    result = await collection.insert_one(safe_data)
except DuplicateKeyError as e:
    field_name = list(e.details.get('keyPattern', {}).keys())[0]
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f'{field_name} already exists'
    )

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f'[UNHANDLED ERROR] {str(exc)}')
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            'success': False,
            'message': (
                'Internal Server Error'
                if settings.environment == 'production'
                else str(exc)
            )
        }
    )

# Request-level error handling
@app.middleware('http')
async def log_requests(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f'[ERROR] {request.method} {request.url.path} — {str(e)}')
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'success': False, 'message': str(e)}
        )
```

### Key Differences
| Aspect | Express | FastAPI |
|--------|---------|---------|
| **Validation Errors** | Manual checks, return response | Automatic, raises exception |
| **Exception Flow** | `next(error)` to handler | `raise HTTPException()` |
| **Status Code** | Integer (200, 400, etc.) | `status.HTTP_*` constants |
| **Response Body** | Manual JSON object | Auto-serialized from dict |
| **Logging** | Manual console.error | Logger module |
| **Environment Check** | Ternary inline | Dedicated settings |

---

## Summary: When to Use Which Pattern

### Express (Node.js)
- ✅ Already running a Node.js stack
- ✅ Team expertise in JavaScript
- ✅ Need lightweight framework
- ✅ Simple callback-based middleware

### FastAPI (Python)
- ✅ Need async/concurrent operations
- ✅ Team expertise in Python
- ✅ Want automatic API documentation
- ✅ Prefer type safety (mypy, Pydantic)
- ✅ Need high performance with fewer resources
- ✅ Want modern async/await pattern

**This migration chose FastAPI for:**
- Native async operations with Motor
- Type-safe models with Pydantic
- Automatic OpenAPI/Swagger docs
- Better developer experience with fast reload
- Python ecosystem for data processing
