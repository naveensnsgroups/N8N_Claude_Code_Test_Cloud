"""
CRUD operations for Employee collection.
Equivalent to Express controller operations.
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from models import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

COLLECTION_NAME = "HR"
ALLOWED_FIELDS = {
    'fullName', 'employeeId', 'email', 'phone',
    'dateOfBirth', 'gender', 'address',
    'department', 'position', 'joinDate',
}


def pick_fields(data: dict) -> dict:
    """
    Pick only allowed fields from request data (prevents mass assignment).
    Converts snake_case to camelCase for MongoDB storage.
    """
    field_mapping = {
        'full_name': 'fullName',
        'employee_id': 'employeeId',
        'date_of_birth': 'dateOfBirth',
        'join_date': 'joinDate',
    }

    result = {}
    for key, value in data.items():
        if key in field_mapping:
            mongo_key = field_mapping[key]
        else:
            mongo_key = key

        if value is not None:
            if isinstance(value, str):
                result[mongo_key] = value.strip()
                if mongo_key == 'email':
                    result[mongo_key] = result[mongo_key].lower()
            else:
                result[mongo_key] = value

    return result


def is_valid_object_id(id_str: str) -> bool:
    """Check if string is a valid MongoDB ObjectId."""
    try:
        ObjectId(id_str)
        return True
    except Exception:
        return False


async def get_all_employees(
    db: AsyncIOMotorDatabase,
    page: int = 1,
    limit: int = 50
) -> dict:
    """
    Get paginated list of all employees.
    @route   GET /api/employees
    """
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

    # Convert ObjectId to string for JSON serialization
    for emp in employees:
        emp['_id'] = str(emp['_id'])

    return {
        'success': True,
        'count': len(employees),
        'total': total,
        'page': page,
        'pages': (total + limit - 1) // limit,  # Ceiling division
        'data': employees,
    }


async def get_employee_by_id(db: AsyncIOMotorDatabase, employee_id: str) -> dict:
    """
    Get a single employee by ID.
    @route   GET /api/employees/:id
    """
    if not is_valid_object_id(employee_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid employee ID format'
        )

    collection = db[COLLECTION_NAME]
    employee = await collection.find_one({'_id': ObjectId(employee_id)})

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Employee not found'
        )

    employee['_id'] = str(employee['_id'])
    return {'success': True, 'data': employee}


async def create_employee(db: AsyncIOMotorDatabase, employee_data: EmployeeCreate) -> dict:
    """
    Create a new employee.
    @route   POST /api/employees
    """
    collection = db[COLLECTION_NAME]

    # Convert Pydantic model to dict and pick allowed fields
    data_dict = employee_data.model_dump(exclude_unset=True)
    safe_data = pick_fields(data_dict)

    try:
        result = await collection.insert_one(safe_data)

        # Fetch the created document
        created_employee = await collection.find_one({'_id': result.inserted_id})
        created_employee['_id'] = str(created_employee['_id'])

        return {
            'success': True,
            'message': 'Employee created successfully',
            'data': created_employee
        }
    except DuplicateKeyError as e:
        # Extract the field name from the duplicate key error
        field_name = list(e.details.get('keyPattern', {}).keys())[0] if e.details else 'field'
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'{field_name} already exists'
        )


async def update_employee(
    db: AsyncIOMotorDatabase,
    employee_id: str,
    employee_data: EmployeeUpdate
) -> dict:
    """
    Update an existing employee.
    @route   PUT /api/employees/:id
    """
    if not is_valid_object_id(employee_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid employee ID format'
        )

    collection = db[COLLECTION_NAME]

    # Convert to dict and pick allowed fields
    data_dict = employee_data.model_dump(exclude_unset=True, exclude_none=True)
    safe_data = pick_fields(data_dict)

    if not safe_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No valid fields to update'
        )

    try:
        result = await collection.find_one_and_update(
            {'_id': ObjectId(employee_id)},
            {'$set': safe_data},
            return_document=True
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Employee not found'
            )

        result['_id'] = str(result['_id'])
        return {
            'success': True,
            'message': 'Employee updated successfully',
            'data': result
        }
    except DuplicateKeyError as e:
        field_name = list(e.details.get('keyPattern', {}).keys())[0] if e.details else 'field'
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'{field_name} already exists'
        )


async def delete_employee(db: AsyncIOMotorDatabase, employee_id: str) -> dict:
    """
    Delete an employee.
    @route   DELETE /api/employees/:id
    """
    if not is_valid_object_id(employee_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid employee ID format'
        )

    collection = db[COLLECTION_NAME]
    result = await collection.find_one_and_delete({'_id': ObjectId(employee_id)})

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Employee not found'
        )

    return {'success': True, 'message': 'Employee deleted successfully'}
