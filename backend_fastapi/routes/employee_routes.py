"""
Employee API routes.
Equivalent to Express employeeRoutes.js
"""
from fastapi import APIRouter, Depends, Query, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from motor.motor_asyncio import AsyncDatabase

from database import get_database
from models import EmployeeCreate, EmployeeUpdate, EmployeeResponse, PaginatedEmployeeResponse
from crud import (
    get_all_employees,
    get_employee_by_id,
    create_employee,
    update_employee,
    delete_employee,
)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get(
    '',
    response_model=PaginatedEmployeeResponse,
    status_code=status.HTTP_200_OK,
    summary='Get all employees',
    description='Retrieve a paginated list of all employees'
)
@limiter.limit('100/15minutes')
async def list_employees(
    page: int = Query(1, ge=1, description='Page number (starting from 1)'),
    limit: int = Query(50, ge=1, le=100, description='Number of records per page'),
    db: AsyncDatabase = Depends(get_database)
):
    """
    Get all employees with pagination.

    **Parameters:**
    - `page`: Page number (default: 1)
    - `limit`: Records per page, max 100 (default: 50)

    **Returns:** Paginated list of employees
    """
    return await get_all_employees(db, page, limit)


@router.get(
    '/{employee_id}',
    status_code=status.HTTP_200_OK,
    summary='Get employee by ID',
    description='Retrieve a single employee by their MongoDB ObjectId'
)
@limiter.limit('100/15minutes')
async def retrieve_employee(
    employee_id: str,
    db: AsyncDatabase = Depends(get_database)
):
    """
    Get a single employee by ID.

    **Parameters:**
    - `employee_id`: MongoDB ObjectId of the employee

    **Returns:** Employee data if found, otherwise 404 error
    """
    return await get_employee_by_id(db, employee_id)


@router.post(
    '',
    status_code=status.HTTP_201_CREATED,
    summary='Create new employee',
    description='Create a new employee record with validation'
)
@limiter.limit('100/15minutes')
async def create_new_employee(
    employee_data: EmployeeCreate,
    db: AsyncDatabase = Depends(get_database)
):
    """
    Create a new employee.

    **Request Body:**
    - `full_name`: Full name (letters and spaces only, max 100 chars)
    - `employee_id`: Unique employee ID (format: EMP + digits, e.g., EMP001)
    - `email`: Email address (must end with @snsgroups.com)
    - `phone`: Phone number (exactly 10 digits)
    - `date_of_birth`: Optional date of birth
    - `gender`: Optional (Male, Female, or Other)
    - `address`: Optional street address
    - `department`: Optional department
    - `position`: Optional job position
    - `join_date`: Optional join date

    **Returns:** Created employee with HTTP 201 status
    """
    return await create_employee(db, employee_data)


@router.put(
    '/{employee_id}',
    status_code=status.HTTP_200_OK,
    summary='Update employee',
    description='Update an existing employee record'
)
@limiter.limit('100/15minutes')
async def update_existing_employee(
    employee_id: str,
    employee_data: EmployeeUpdate,
    db: AsyncDatabase = Depends(get_database)
):
    """
    Update an existing employee.

    **Parameters:**
    - `employee_id`: MongoDB ObjectId of the employee

    **Request Body:** All fields are optional. Only provided fields will be updated.

    **Returns:** Updated employee data
    """
    return await update_employee(db, employee_id, employee_data)


@router.delete(
    '/{employee_id}',
    status_code=status.HTTP_200_OK,
    summary='Delete employee',
    description='Delete an employee record by ID'
)
@limiter.limit('100/15minutes')
async def delete_existing_employee(
    employee_id: str,
    db: AsyncDatabase = Depends(get_database)
):
    """
    Delete an employee.

    **Parameters:**
    - `employee_id`: MongoDB ObjectId of the employee

    **Returns:** Success message if deletion was successful
    """
    return await delete_employee(db, employee_id)
