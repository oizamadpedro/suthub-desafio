import boto3
import os
from typing import List, Optional
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from .domain import AgeGroup, Enrollment

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb")
        self.age_groups_table = self.dynamodb.Table(os.getenv("AGE_GROUPS_TABLE", "age-groups"))
        self.enrollments_table = self.dynamodb.Table(os.getenv("ENROLLMENTS_TABLE", "enrollments"))
    
    # Age Groups operations
    
    def create_age_group(self, age_group: AgeGroup) -> AgeGroup:
        """Create a new age group"""
        try:
            self.age_groups_table.put_item(
                Item=age_group.to_dict(),
                ConditionExpression='attribute_not_exists(id)'
            )
            return age_group
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError("Age group with this ID already exists")
            raise e
    
    def get_age_group(self, age_group_id: str) -> Optional[AgeGroup]:
        """Get age group by ID"""
        try:
            response = self.age_groups_table.get_item(Key={"id": age_group_id})
            if "Item" in response:
                return AgeGroup.from_dict(response["Item"])
            return None
        except ClientError:
            return None
    
    def list_age_groups(self) -> List[AgeGroup]:
        """List all age groups"""
        try:
            response = self.age_groups_table.scan()
            return [AgeGroup.from_dict(item) for item in response.get("Items", [])]
        except ClientError:
            return []
    
    def update_age_group(self, age_group: AgeGroup) -> AgeGroup:
        """Update an existing age group"""
        try:
            self.age_groups_table.put_item(
                Item=age_group.to_dict(),
                ConditionExpression='attribute_exists(id)'
            )
            return age_group
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError("Age group not found")
            raise e
    
    def delete_age_group(self, age_group_id: str) -> bool:
        """Delete an age group"""
        try:
            self.age_groups_table.delete_item(
                Key={"id": age_group_id},
                ConditionExpression='attribute_exists(id)'
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False
            raise e
    
    def find_age_group_for_age(self, age: int) -> Optional[AgeGroup]:
        """Find the appropriate age group for a given age"""
        age_groups = self.list_age_groups()
        for age_group in age_groups:
            if age_group.contains_age(age):
                return age_group
        return None
    
    # Enrollment operations
    
    def create_enrollment(self, enrollment: Enrollment) -> Enrollment:
        """Create a new enrollment"""
        try:
            self.enrollments_table.put_item(
                Item=enrollment.to_dict(),
                ConditionExpression='attribute_not_exists(cpf)'
            )
            return enrollment
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError("Enrollment with this CPF already exists")
            raise e
    
    def get_enrollment(self, cpf: str) -> Optional[Enrollment]:
        """Get enrollment by CPF"""
        try:
            response = self.enrollments_table.get_item(Key={"cpf": cpf})
            if "Item" in response:
                return Enrollment.from_dict(response["Item"])
            return None
        except ClientError:
            return None
    
    def list_enrollments(self) -> List[Enrollment]:
        """List all enrollments"""
        try:
            response = self.enrollments_table.scan()
            return [Enrollment.from_dict(item) for item in response.get("Items", [])]
        except ClientError:
            return []
    
    def delete_enrollment(self, cpf: str) -> bool:
        """Delete an enrollment"""
        try:
            self.enrollments_table.delete_item(
                Key={"cpf": cpf},
                ConditionExpression='attribute_exists(cpf)'
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False
            raise e