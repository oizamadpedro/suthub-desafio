from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
import uuid

@dataclass
class AgeGroup:

    name: str
    min_age: int
    max_age: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: Optional[str] = None
    
    def update(self, name: Optional[str] = None, min_age: Optional[int] = None, max_age: Optional[int] = None):

        if name is not None:
            self.name = name
        if min_age is not None:
            self.min_age = min_age
        if max_age is not None:
            self.max_age = max_age
        self.updated_at = datetime.utcnow().isoformat()
    
    def contains_age(self, age: int) -> bool:
        return self.min_age <= age <= self.max_age
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "min_age": self.min_age,
            "max_age": self.max_age,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AgeGroup':
        return cls(
            id=data["id"],
            name=data["name"],
            min_age=int(data["min_age"]),
            max_age=int(data["max_age"]),
            created_at=data["created_at"],
            updated_at=data.get("updated_at")
        )

@dataclass
class Enrollment:
    """Internal dataclass for enrollment management"""
    name: str
    age: int
    cpf: str
    age_group_id: str
    age_group_name: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "cpf": self.cpf,
            "name": self.name,
            "age": self.age,
            "age_group_id": self.age_group_id,
            "age_group_name": self.age_group_name,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Enrollment':
        return cls(
            cpf=data["cpf"],
            name=data["name"],
            age=int(data["age"]),
            age_group_id=data["age_group_id"],
            age_group_name=data["age_group_name"],
            created_at=data["created_at"]
        )