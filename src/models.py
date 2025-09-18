from pydantic import BaseModel, Field, validator
from typing import Optional
from .validators import validate_cpf, validate_name, clean_cpf

class AgeGroupCreateRequest(BaseModel):
    """Pydantic model for creating age groups"""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the age group")
    min_age: int = Field(..., ge=0, le=120, description="Minimum age for the group")
    max_age: int = Field(..., ge=0, le=120, description="Maximum age for the group")
    
    @validator('max_age')
    def validate_age_range(cls, max_age, values):
        min_age = values.get('min_age')
        if min_age is not None and max_age < min_age:
            raise ValueError('max_age must be greater than or equal to min_age')
        return max_age

class AgeGroupUpdateRequest(BaseModel):
    """Pydantic model for updating age groups"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the age group")
    min_age: Optional[int] = Field(None, ge=0, le=120, description="Minimum age for the group")
    max_age: Optional[int] = Field(None, ge=0, le=120, description="Maximum age for the group")
    
    @validator('max_age')
    def validate_age_range(cls, max_age, values):
        min_age = values.get('min_age')
        if min_age is not None and max_age is not None and max_age < min_age:
            raise ValueError('max_age must be greater than or equal to min_age')
        return max_age

class EnrollmentRequest(BaseModel):
    """Pydantic model for enrollment requests"""
    name: str = Field(..., min_length=1, max_length=200, description="Full name of the person")
    age: int = Field(..., ge=0, le=120, description="Age of the person")
    cpf: str = Field(..., min_length=11, max_length=14, description="CPF number")
    
    @validator('cpf')
    def validate_cpf_field(cls, cpf):
        cpf_clean = clean_cpf(cpf)
        
        if not validate_cpf(cpf_clean):
            raise ValueError('Invalid CPF number')
        
        return cpf_clean
    
    @validator('name')
    def validate_name_field(cls, name):
        name = name.strip()
        
        if not validate_name(name):
            raise ValueError('Name must contain at least first and last name with minimum 2 characters each')
        
        return name

class AgeGroupResponse(BaseModel):
    """Response model for age group data"""
    id: str
    name: str
    min_age: int
    max_age: int
    created_at: str
    updated_at: Optional[str] = None

class EnrollmentResponse(BaseModel):
    """Response model for enrollment data"""
    cpf: str
    name: str
    age: int
    age_group: str
    created_at: str