import re
from typing import List

def validate_cpf(cpf: str) -> bool:
    """
    Validate Brazilian CPF number
    Returns True if CPF is valid, False otherwise
    """
    # Remove non-numeric characters
    cpf = re.sub(r'\D', '', cpf)
    
    # Check if has 11 digits
    if len(cpf) != 11:
        return False
    
    # Check if all digits are the same
    if cpf == cpf[0] * 11:
        return False
    
    # Calculate first verification digit
    sum1 = 0
    for i in range(9):
        sum1 += int(cpf[i]) * (10 - i)
    
    remainder1 = sum1 % 11
    digit1 = 0 if remainder1 < 2 else 11 - remainder1
    
    # Check first verification digit
    if int(cpf[9]) != digit1:
        return False
    
    # Calculate second verification digit
    sum2 = 0
    for i in range(10):
        sum2 += int(cpf[i]) * (11 - i)
    
    remainder2 = sum2 % 11
    digit2 = 0 if remainder2 < 2 else 11 - remainder2
    
    # Check second verification digit
    if int(cpf[10]) != digit2:
        return False
    
    return True

def format_cpf(cpf: str) -> str:
    """Format CPF with dots and dash"""
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf

def clean_cpf(cpf: str) -> str:
    """Remove formatting from CPF, keeping only numbers"""
    return re.sub(r'\D', '', cpf)

def validate_name(name: str) -> bool:
    """
    Validate person name
    Must have at least first and last name
    """
    name = name.strip()
    if not name:
        return False
    
    # Check if has at least 2 words (first and last name)
    name_parts = name.split()
    if len(name_parts) < 2:
        return False
    
    # Check if all parts have at least 2 characters
    for part in name_parts:
        if len(part) < 2:
            return False
    
    # Check if contains only letters and spaces
    if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', name):
        return False
    
    return True

def validate_age_in_groups(age: int, age_groups: List) -> tuple[bool, str]:
    """
    Validate if age fits in any available age group
    Returns tuple (is_valid, error_message or group_name)
    """
    if not age_groups:
        return False, "No age groups configured"
    
    for group in age_groups:
        if group.contains_age(age):
            return True, group.name
    
    # Find the closest age groups to give better error message
    younger_groups = [g for g in age_groups if g.max_age < age]
    older_groups = [g for g in age_groups if g.min_age > age]
    
    if younger_groups and older_groups:
        max_younger = max(younger_groups, key=lambda g: g.max_age)
        min_older = min(older_groups, key=lambda g: g.min_age)
        return False, f"Age {age} doesn't fit any group. Closest groups: {max_younger.name} (up to {max_younger.max_age}) and {min_older.name} (from {min_older.min_age})"
    elif younger_groups:
        max_younger = max(younger_groups, key=lambda g: g.max_age)
        return False, f"Age {age} is too high. Maximum age in available groups is {max_younger.max_age} ({max_younger.name})"
    elif older_groups:
        min_older = min(older_groups, key=lambda g: g.min_age)
        return False, f"Age {age} is too low. Minimum age in available groups is {min_older.min_age} ({min_older.name})"
    else:
        return False, f"Age {age} doesn't fit any configured age group"