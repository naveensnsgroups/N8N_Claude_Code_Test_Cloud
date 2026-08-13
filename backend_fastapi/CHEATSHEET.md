# FastAPI Backend - Quick Reference Cheatsheet

## Startup

```bash
# Development (with auto-reload)
uvicorn main:app --reload

# Production (4 workers)
uvicorn main:app --workers 4

# Custom port
uvicorn main:app --port 8000
```

## API Endpoints

### Health
```
GET /
```

### Employees
```
GET    /api/employees              # List all (paginated)
POST   /api/employees              # Create new
GET    /api/employees/{id}         # Get single
PUT    /api/employees/{id}         # Update
DELETE /api/employees/{id}         # Delete
```

## Query Parameters

```
GET /api/employees?page=1&limit=50
    page  - Page number (default: 1)
    limit - Per page, max 100 (default: 50)
```

## Required Fields for Create/Update

### Create (POST)
```json
{
  "full_name": "John Doe",           // Required
  "employee_id": "EMP001",           // Required, unique
  "email": "john@snsgroups.com",     // Required, unique
  "phone": "9876543210"              // Required
}
```

### Update (PUT)
```json
{
  "position": "Engineer"             // Any field, optional
}
```

## Validation Rules

| Field | Rule |
|-------|------|
| `full_name` | Letters & spaces only, max 100 chars |
| `employee_id` | Format: EMP + digits, unique, max 20 chars |
| `email` | Must end with @snsgroups.com, unique |
| `phone` | Exactly 10 digits |
| `gender` | Male, Female, or Other |
| `department` | IT, HR, Finance, Marketing, Operations, Sales, Admin, Other |

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success (GET, PUT, DELETE) |
| 201 | Created (POST) |
| 400 | Bad request / Invalid input |
| 404 | Not found |
| 409 | Conflict (duplicate unique field) |
| 422 | Validation error |
| 429 | Rate limit exceeded |
| 500 | Server error |

## Common cURL Commands

### Health Check
```bash
curl http://localhost:5000/
```

### List Employees
```bash
curl "http://localhost:5000/api/employees?page=1&limit=10"
```

### Create Employee
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

### Get Single Employee
```bash
curl http://localhost:5000/api/employees/{id}
```

### Update Employee
```bash
curl -X PUT http://localhost:5000/api/employees/{id} \
  -H "Content-Type: application/json" \
  -d '{"position": "Engineer"}'
```

### Delete Employee
```bash
curl -X DELETE http://localhost:5000/api/employees/{id}
```

## Environment Variables

```bash
MONGO_URI=mongodb+srv://...         # MongoDB connection
PORT=5000                            # Server port
HOST=0.0.0.0                         # Server host
NODE_ENV=development                 # Environment
CLIENT_URL=http://localhost:5173     # CORS origin
```

## File Structure Reference

```
main.py              # FastAPI app setup
config.py            # Settings & configuration
database.py          # MongoDB connection
models.py            # Pydantic schemas
crud.py              # Database operations
routes/
  └─ employee_routes.py  # API endpoints
```

## Response Format

### Success (200, 201)
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... },
  "count": 10,
  "total": 100,
  "page": 1,
  "pages": 10
}
```

### Error (400, 404, 409, etc.)
```json
{
  "success": false,
  "message": "Error description"
}
```

### Validation Error (422)
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "Email must end with @snsgroups.com domain"
    }
  ]
}
```

## API Documentation

- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc
- **OpenAPI JSON**: http://localhost:5000/openapi.json

## Rate Limiting

- **Limit**: 100 requests per 15 minutes
- **Per**: Client IP address
- **Error**: 429 Too Many Requests

## Common Issues & Solutions

### Port Already in Use
```bash
# Use different port
uvicorn main:app --port 8000
```

### MongoDB Connection Failed
```bash
# Check MONGO_URI in .env
# Verify IP whitelisted in MongoDB Atlas
# Test connection: python -c "from motor.motor_asyncio import AsyncClient; ..."
```

### Email Validation Failed
```bash
# Must use exactly: @snsgroups.com
# Must be lowercase
# Example: john.doe@snsgroups.com ✅
```

### Phone Validation Failed
```bash
# Must be exactly 10 digits
# No spaces, hyphens, or country codes
# Example: 9876543210 ✅ vs 987-654-3210 ❌
```

## Testing

### Run Tests
```bash
pytest test_main.py -v
```

### Quick Health Check
```bash
curl http://localhost:5000/
```

### Load Test
```bash
# 1000 requests, 10 concurrent
ab -n 1000 -c 10 http://localhost:5000/
```

## Development Workflow

1. **Edit code** in any file
2. **Server auto-reloads** (with `--reload`)
3. **Visit /docs** to test endpoint
4. **Check logs** for errors
5. **Commit changes** when ready

## Code Organization

### `main.py`
- FastAPI app
- Middleware setup
- Route registration
- Error handlers
- Lifespan events

### `config.py`
- Environment settings
- Configuration values
- Defaults

### `database.py`
- MongoDB connection
- Connection management
- Global database instance

### `models.py`
- Pydantic models
- Validation logic
- Request/response schemas

### `crud.py`
- Database operations
- Business logic
- Data transformation

### `routes/employee_routes.py`
- API endpoints
- Request handlers
- Response serialization

## Pydantic Models

### EmployeeCreate
For POST requests (all fields required)

### EmployeeUpdate
For PUT requests (all fields optional)

### EmployeeResponse
For GET responses (includes timestamps and _id)

### PaginatedEmployeeResponse
For paginated list responses (includes page info)

## Dependency Injection

### Get Database
```python
async def endpoint(
    db: AsyncDatabase = Depends(get_database)
):
    # Use db to query
    collection = db["HR"]
```

## MongoDB Collection

- **Name**: `HR`
- **Field Names**: camelCase (for Express compatibility)
- **Unique Fields**: `employeeId`, `email`
- **Timestamps**: `createdAt`, `updatedAt`

## ObjectId Handling

- **Input**: String from URL path
- **Validation**: `is_valid_object_id(id_string)`
- **Conversion**: `ObjectId(id_string)` for queries
- **Output**: Convert to string `str(doc['_id'])`

## Error Handling Pattern

```python
try:
    # Operation
    result = await collection.insert_one(data)
except DuplicateKeyError as e:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Field already exists"
    )
except Exception as e:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=str(e)
    )
```

## Validation Pattern

```python
@field_validator('email', mode='before')
@classmethod
def validate_email(cls, v):
    if v and not v.endswith('@snsgroups.com'):
        raise ValueError('Must end with @snsgroups.com')
    return v
```

## Quick Deployment

### Heroku
```bash
pip freeze > requirements.txt
echo 'web: gunicorn main:app --worker-class uvicorn.workers.UvicornWorker' > Procfile
git push heroku main
```

### Docker
```bash
docker build -t employee-api .
docker run -p 5000:5000 employee-api
```

### Local to Production
```bash
# Set environment variables
export MONGO_URI=your_production_uri
export NODE_ENV=production

# Run with multiple workers
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:5000
```

## Performance Tips

1. **Connection pooling**: Enabled by default in Motor
2. **Async operations**: All I/O is non-blocking
3. **Multiple workers**: Use `--workers 4` for production
4. **Caching**: Add Redis for frequent queries
5. **Database indices**: Unique constraints are indexed

## Debugging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Server Health
```bash
curl -v http://localhost:5000/
```

### View MongoDB Connection
```python
import asyncio
from database import connect_to_mongo

async def test():
    db = await connect_to_mongo()
    print("Connected!")

asyncio.run(test())
```

## Useful Links

- **Local**: http://localhost:5000/docs
- **Swagger**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc
- **OpenAPI**: http://localhost:5000/openapi.json

## Key Differences from Express

| Feature | Express | FastAPI |
|---------|---------|---------|
| Validation | Zod | Pydantic |
| Database | Mongoose | Motor |
| Async | Callbacks | Native async/await |
| Docs | Manual | Auto-generated |
| Status Codes | Implicit | Explicit |
| Type Safety | Limited | Full (mypy) |

## Remember

- 📚 Read `README.md` for full docs
- 🚀 Use `/docs` for interactive testing
- 🔍 Check `TESTING_GUIDE.md` for test cases
- 📖 See `MIGRATION_GUIDE.md` for Express mapping
- 💡 Use `CODE_COMPARISON.md` for code examples

---

**Need Help?** Check the full documentation files or inline code comments.
