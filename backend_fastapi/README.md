# Personal Details API - FastAPI Backend

FastAPI + Motor (async MongoDB) implementation of the Personal Details Management System backend. This is a direct migration from the Express.js backend.

## Features

- ✅ **FastAPI Framework**: Modern, fast async web framework
- ✅ **Motor (Async MongoDB)**: Non-blocking MongoDB driver for async operations
- ✅ **Pydantic Validation**: Strong data validation with Pydantic models
- ✅ **CORS Support**: Configurable CORS for frontend integration
- ✅ **Rate Limiting**: Built-in rate limiting (100 requests per 15 minutes)
- ✅ **Security**: CORS, rate limiting, request validation
- ✅ **Request Logging**: Comprehensive logging for debugging
- ✅ **Error Handling**: Centralized error handling with meaningful responses
- ✅ **MongoDB Integration**: Connection pooling and async operations

## Project Structure

```
backend_fastapi/
├── main.py              # FastAPI app initialization, middleware, and lifespan events
├── config.py            # Configuration management (environment variables)
├── database.py          # MongoDB connection and database utilities
├── models.py            # Pydantic models for validation and serialization
├── crud.py              # CRUD operations for Employee collection
├── routes/
│   └── employee_routes.py  # Employee API endpoints
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
└── README.md            # This file
```

## Installation

### Prerequisites
- Python 3.8+
- MongoDB Atlas account or local MongoDB instance

### Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your MongoDB URI and other settings.

## Running the Server

### Development Mode (with auto-reload)
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --workers 4
```

The API will be available at `http://localhost:5000`

## API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:5000/docs`
- **ReDoc**: `http://localhost:5000/redoc`

### Endpoints

#### Health Check
```http
GET /
```

#### Get All Employees (Paginated)
```http
GET /api/employees?page=1&limit=50
```

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `limit` (integer, default: 50, max: 100): Records per page

**Response:**
```json
{
  "success": true,
  "count": 10,
  "total": 100,
  "page": 1,
  "pages": 10,
  "data": [...]
}
```

#### Get Employee by ID
```http
GET /api/employees/{employee_id}
```

**Response:**
```json
{
  "success": true,
  "data": { ... }
}
```

#### Create Employee
```http
POST /api/employees
Content-Type: application/json

{
  "full_name": "John Doe",
  "employee_id": "EMP001",
  "email": "john.doe@snsgroups.com",
  "phone": "9876543210",
  "date_of_birth": "1990-01-15T00:00:00",
  "gender": "Male",
  "address": "123 Main St",
  "department": "IT",
  "position": "Software Engineer",
  "join_date": "2023-01-15T00:00:00"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Employee created successfully",
  "data": { ... }
}
```

#### Update Employee
```http
PUT /api/employees/{employee_id}
Content-Type: application/json

{
  "full_name": "Jane Doe",
  "position": "Senior Engineer"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Employee updated successfully",
  "data": { ... }
}
```

#### Delete Employee
```http
DELETE /api/employees/{employee_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Employee deleted successfully"
}
```

## Validation Rules

### Full Name
- Required
- Letters and spaces only
- Maximum 100 characters

### Employee ID
- Required
- Format: `EMP` followed by digits (e.g., `EMP001`)
- Unique
- Maximum 20 characters

### Email
- Required
- Must end with `@snsgroups.com`
- Unique
- Maximum 150 characters
- Automatically converted to lowercase

### Phone
- Required
- Exactly 10 digits
- No special characters or spaces

### Optional Fields
- `date_of_birth`: ISO datetime format
- `gender`: "Male", "Female", or "Other"
- `address`: Maximum 500 characters
- `department`: IT, HR, Finance, Marketing, Operations, Sales, Admin, or Other
- `position`: Maximum 100 characters
- `join_date`: ISO datetime format

## Error Handling

The API returns consistent error responses:

```json
{
  "success": false,
  "message": "Error description here"
}
```

### Common Error Codes
- `400 Bad Request`: Invalid input or validation failure
- `404 Not Found`: Employee not found
- `409 Conflict`: Duplicate unique field (email, employee_id)
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Security Features

### CORS (Cross-Origin Resource Sharing)
- Configured via `CLIENT_URL` environment variable
- Supports multiple origins (comma-separated)
- Methods allowed: GET, POST, PUT, DELETE

### Rate Limiting
- 100 requests per 15 minutes per IP address
- Applied to all `/api` endpoints

### Input Validation
- Pydantic models validate all inputs
- NoSQL injection prevention through validation
- Field whitelisting in CRUD operations

### Data Sanitization
- String fields are trimmed
- Email fields automatically converted to lowercase
- Only whitelisted fields are persisted

## Migration Notes from Express

### Key Differences

| Express | FastAPI |
|---------|---------|
| Mongoose Schema | Pydantic Models |
| Middleware stacks | FastAPI middleware + dependencies |
| try/catch + next() | Async/await with exception handlers |
| express-rate-limit | slowapi |
| express-mongo-sanitize | Pydantic validation |
| Callback-based | Async/await native |

### Field Name Changes
For database compatibility, Pydantic fields use snake_case but are automatically converted to camelCase for MongoDB:
- `full_name` → `fullName`
- `employee_id` → `employeeId`
- `date_of_birth` → `dateOfBirth`
- `join_date` → `joinDate`

### Database Collection
- Collection name: `HR` (same as Express version)
- Database connection: MongoDB Atlas (configurable via `MONGO_URI`)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGO_URI` | MongoDB connection string | mongodb://localhost:27017 |
| `PORT` | Server port | 5000 |
| `HOST` | Server host | 0.0.0.0 |
| `NODE_ENV` | Environment mode | development |
| `CLIENT_URL` | Frontend CORS origin | http://localhost:5173 |

## Development

### Running Tests
```bash
# To add pytest tests, install:
pip install pytest pytest-asyncio httpx
```

### Code Quality
```bash
# Format code
pip install black
black .

# Linting
pip install flake8
flake8 .

# Type checking
pip install mypy
mypy .
```

## License

MIT

## Support

For issues or questions about the migration, refer to the original Express implementation in the `backend/` folder for comparison.
