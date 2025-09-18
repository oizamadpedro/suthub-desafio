import os
import boto3
from fastapi import FastAPI, HTTPException, Depends, status
from typing import List
from mangum import Mangum

from .config import Settings
from .auth import verify_config_user, verify_final_user
from .models import (
    AgeGroupCreateRequest, 
    AgeGroupUpdateRequest, 
    AgeGroupResponse,
    EnrollmentRequest,
    EnrollmentResponse
)
from .domain import AgeGroup, Enrollment
from .database import DatabaseService

app = FastAPI(title="Age Groups and Enrollment API", version="1.0.0")
setting = Settings(env="env.dev")
sqs = boto3.client("sqs")
QUEUE_URL = os.getenv("QUEUE_URL")
db_service = DatabaseService()

@app.get("/hello")
async def root():
    return {"message": f"Hello World {setting.env}"}

# Configuration User Endpoints (Age Groups Management)

@app.post("/config/age-groups", response_model=AgeGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_age_group(
    age_group_data: AgeGroupCreateRequest,
    current_user: str = Depends(verify_config_user)
):
    """Create a new age group (Configuration User only)"""
    try:
        # Check for overlapping age ranges
        existing_groups = db_service.list_age_groups()
        for existing in existing_groups:
            if (age_group_data.min_age <= existing.max_age and 
                age_group_data.max_age >= existing.min_age):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Age range overlaps with existing group: {existing.name}"
                )
        
        age_group = AgeGroup(
            name=age_group_data.name,
            min_age=age_group_data.min_age,
            max_age=age_group_data.max_age
        )
        
        created_group = db_service.create_age_group(age_group)
        
        return AgeGroupResponse(
            id=created_group.id,
            name=created_group.name,
            min_age=created_group.min_age,
            max_age=created_group.max_age,
            created_at=created_group.created_at,
            updated_at=created_group.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/config/age-groups", response_model=List[AgeGroupResponse])
async def list_age_groups(current_user: str = Depends(verify_config_user)):
    """List all age groups (Configuration User only)"""
    age_groups = db_service.list_age_groups()
    return [
        AgeGroupResponse(
            id=ag.id,
            name=ag.name,
            min_age=ag.min_age,
            max_age=ag.max_age,
            created_at=ag.created_at,
            updated_at=ag.updated_at
        )
        for ag in age_groups
    ]

@app.get("/config/age-groups/{age_group_id}", response_model=AgeGroupResponse)
async def get_age_group(
    age_group_id: str,
    current_user: str = Depends(verify_config_user)
):
    """Get specific age group by ID (Configuration User only)"""
    age_group = db_service.get_age_group(age_group_id)
    if not age_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Age group not found"
        )
    
    return AgeGroupResponse(
        id=age_group.id,
        name=age_group.name,
        min_age=age_group.min_age,
        max_age=age_group.max_age,
        created_at=age_group.created_at,
        updated_at=age_group.updated_at
    )

@app.put("/config/age-groups/{age_group_id}", response_model=AgeGroupResponse)
async def update_age_group(
    age_group_id: str,
    age_group_data: AgeGroupUpdateRequest,
    current_user: str = Depends(verify_config_user)
):
    """Update age group (Configuration User only)"""
    try:
        age_group = db_service.get_age_group(age_group_id)
        if not age_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Age group not found"
            )
        
        # Update fields if provided
        age_group.update(
            name=age_group_data.name,
            min_age=age_group_data.min_age,
            max_age=age_group_data.max_age
        )
        
        # Check for overlapping age ranges with other groups
        existing_groups = db_service.list_age_groups()
        for existing in existing_groups:
            if existing.id != age_group.id:
                if (age_group.min_age <= existing.max_age and 
                    age_group.max_age >= existing.min_age):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Age range overlaps with existing group: {existing.name}"
                    )
        
        updated_group = db_service.update_age_group(age_group)
        
        return AgeGroupResponse(
            id=updated_group.id,
            name=updated_group.name,
            min_age=updated_group.min_age,
            max_age=updated_group.max_age,
            created_at=updated_group.created_at,
            updated_at=updated_group.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.delete("/config/age-groups/{age_group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_age_group(
    age_group_id: str,
    current_user: str = Depends(verify_config_user)
):
    """Delete age group (Configuration User only)"""
    success = db_service.delete_age_group(age_group_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Age group not found"
        )

# Final User Endpoints (Enrollment)

@app.post("/enroll", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def create_enrollment(
    enrollment_data: EnrollmentRequest,
    current_user: str = Depends(verify_final_user)
):
    """Create new enrollment (Final User and Config User)"""
    try:
        # Check if CPF already exists
        existing_enrollment = db_service.get_enrollment(enrollment_data.cpf)
        if existing_enrollment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF already enrolled"
            )
        
        # Find appropriate age group
        age_group = db_service.find_age_group_for_age(enrollment_data.age)
        if not age_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No age group found for age {enrollment_data.age}. Please contact administrator."
            )
        
        enrollment = Enrollment(
            name=enrollment_data.name,
            age=enrollment_data.age,
            cpf=enrollment_data.cpf,
            age_group_id=age_group.id,
            age_group_name=age_group.name
        )
        
        created_enrollment = db_service.create_enrollment(enrollment)
        
        # Also send to SQS queue if configured (backward compatibility)
        if QUEUE_URL:
            try:
                sqs.send_message(
                    QueueUrl=QUEUE_URL,
                    MessageBody=enrollment_data.json()
                )
            except Exception as e:
                # Log error but don't fail the enrollment
                print(f"Warning: Failed to send to SQS queue: {e}")
        
        return EnrollmentResponse(
            cpf=created_enrollment.cpf,
            name=created_enrollment.name,
            age=created_enrollment.age,
            age_group=created_enrollment.age_group_name,
            created_at=created_enrollment.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/enrollments", response_model=List[EnrollmentResponse])
async def list_enrollments(current_user: str = Depends(verify_final_user)):
    """List all enrollments (Final User and Config User)"""
    enrollments = db_service.list_enrollments()
    return [
        EnrollmentResponse(
            cpf=e.cpf,
            name=e.name,
            age=e.age,
            age_group=e.age_group_name,
            created_at=e.created_at
        )
        for e in enrollments
    ]

@app.get("/enrollments/{cpf}", response_model=EnrollmentResponse)
async def get_enrollment(
    cpf: str,
    current_user: str = Depends(verify_final_user)
):
    """Get enrollment by CPF (Final User and Config User)"""
    enrollment = db_service.get_enrollment(cpf)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    return EnrollmentResponse(
        cpf=enrollment.cpf,
        name=enrollment.name,
        age=enrollment.age,
        age_group=enrollment.age_group_name,
        created_at=enrollment.created_at
    )

@app.delete("/enrollments/{cpf}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(
    cpf: str,
    current_user: str = Depends(verify_final_user)
):
    """Delete enrollment by CPF (Final User and Config User)"""
    success = db_service.delete_enrollment(cpf)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )

# Legacy endpoint for backward compatibility
@app.post("/enroll-legacy")
async def enqueue_enrollment_legacy(enrollment: EnrollmentRequest):
    """Legacy enrollment endpoint for backward compatibility"""
    if not QUEUE_URL:
        return {"error": "QUEUE_URL não configurada"}

    response = sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=enrollment.json()
    )

    return {
        "message": f"Enrollment enviado para fila {QUEUE_URL}",
        "MessageId": response["MessageId"]
    }

handler = Mangum(app)
