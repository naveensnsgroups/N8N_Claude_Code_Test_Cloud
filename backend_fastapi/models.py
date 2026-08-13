"""
Pydantic models for Employee data validation and serialization.
Equivalent to Mongoose schema from the Express backend.
"""
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class GenderEnum(str, Enum):
    """Valid gender values."""
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class DepartmentEnum(str, Enum):
    """Valid department values."""
    IT = "IT"
    HR = "HR"
    FINANCE = "Finance"
    MARKETING = "Marketing"
    OPERATIONS = "Operations"
    SALES = "Sales"
    ADMIN = "Admin"
    OTHER = "Other"


class EmployeeBase(BaseModel):
    """Base employee schema with required fields."""

    full_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Employee full name (letters and spaces only)"
    )
    employee_id: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Unique employee ID (format: EMP followed by numbers, e.g., EMP001)"
    )
    email: EmailStr = Field(
        ...,
        max_length=150,
        description="Email address (must end with @snsgroups.com)"
    )
    phone: str = Field(
        ...,
        min_length=10,
        max_length=10,
        description="Phone number (exactly 10 digits)"
    )
    date_of_birth: Optional[datetime] = Field(
        default=None,
        description="Date of birth"
    )
    gender: Optional[GenderEnum] = Field(
        default=None,
        description="Gender (Male, Female, or Other)"
    )
    address: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Street address"
    )
    department: Optional[DepartmentEnum] = Field(
        default=None,
        description="Department assignment"
    )
    position: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Job position/title"
    )
    join_date: Optional[datetime] = Field(
        default=None,
        description="Employee join date"
    )

    @field_validator('full_name', mode='before')
    @classmethod
    def validate_full_name(cls, v):
        """Validate full name contains only letters and spaces."""
        if v is not None:
            v = v.strip()
            if not all(c.isalpha() or c.isspace() for c in v):
                raise ValueError('Full name must contain only letters and spaces')
        return v

    @field_validator('employee_id', mode='before')
    @classmethod
    def validate_employee_id(cls, v):
        """Validate employee ID format (EMP followed by numbers)."""
        if v is not None:
            v = v.strip()
            if not (v.startswith('EMP') and v[3:].isdigit()):
                raise ValueError('Employee ID must start with EMP followed by numbers (e.g., EMP001)')
        return v

    @field_validator('email', mode='before')
    @classmethod
    def validate_email_domain(cls, v):
        """Validate email ends with @snsgroups.com domain."""
        if v is not None:
            v = v.strip().lower()
            if not v.endswith('@snsgroups.com'):
                raise ValueError('Email must end with @snsgroups.com domain')
        return v

    @field_validator('phone', mode='before')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone is exactly 10 digits."""
        if v is not None:
            v = v.strip()
            if not (v.isdigit() and len(v) == 10):
                raise ValueError('Phone number must be exactly 10 digits')
        return v


class EmployeeCreate(EmployeeBase):
    """Schema for creating a new employee."""
    pass


class EmployeeUpdate(BaseModel):
    """Schema for updating an employee (all fields optional)."""

    full_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100
    )
    employee_id: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=20
    )
    email: Optional[EmailStr] = Field(
        default=None,
        max_length=150
    )
    phone: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=10
    )
    date_of_birth: Optional[datetime] = None
    gender: Optional[GenderEnum] = None
    address: Optional[str] = Field(default=None, max_length=500)
    department: Optional[DepartmentEnum] = None
    position: Optional[str] = Field(default=None, max_length=100)
    join_date: Optional[datetime] = None

    @field_validator('full_name', mode='before')
    @classmethod
    def validate_full_name(cls, v):
        """Validate full name contains only letters and spaces."""
        if v is not None:
            v = v.strip()
            if not all(c.isalpha() or c.isspace() for c in v):
                raise ValueError('Full name must contain only letters and spaces')
        return v

    @field_validator('employee_id', mode='before')
    @classmethod
    def validate_employee_id(cls, v):
        """Validate employee ID format."""
        if v is not None:
            v = v.strip()
            if not (v.startswith('EMP') and v[3:].isdigit()):
                raise ValueError('Employee ID must start with EMP followed by numbers (e.g., EMP001)')
        return v

    @field_validator('email', mode='before')
    @classmethod
    def validate_email_domain(cls, v):
        """Validate email domain."""
        if v is not None:
            v = v.strip().lower()
            if not v.endswith('@snsgroups.com'):
                raise ValueError('Email must end with @snsgroups.com domain')
        return v

    @field_validator('phone', mode='before')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone is exactly 10 digits."""
        if v is not None:
            v = v.strip()
            if not (v.isdigit() and len(v) == 10):
                raise ValueError('Phone number must be exactly 10 digits')
        return v


class EmployeeResponse(EmployeeBase):
    """Schema for employee responses (includes timestamps)."""

    id: str = Field(..., alias='_id', description="MongoDB ObjectId")
    created_at: datetime = Field(..., alias='createdAt')
    updated_at: datetime = Field(..., alias='updatedAt')

    class Config:
        populate_by_name = True
        from_attributes = True


class PaginatedEmployeeResponse(BaseModel):
    """Schema for paginated employee list response."""

    success: bool
    count: int
    total: int
    page: int
    pages: int
    data: list[EmployeeResponse]
