import base64
import os
from typing import Optional, Tuple
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

def load_auth_users() -> dict:
    """Load authentication users from static file"""
    auth_file_path = os.path.join(os.path.dirname(__file__), "auth_users.txt")
    users = {}
    
    try:
        with open(auth_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    username, password = line.split(':', 1)
                    users[username] = password
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication file not found"
        )
    
    return users

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Verify basic auth credentials and return username"""
    users = load_auth_users()
    
    if credentials.username not in users or users[credentials.username] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username

def verify_config_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Verify user has configuration privileges"""
    username = verify_credentials(credentials)
    
    if not username.startswith('config_'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Configuration privileges required"
        )
    
    return username

def verify_final_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Verify user can perform enrollment"""
    username = verify_credentials(credentials)
    
    # Both config and final users can enroll
    if not (username.startswith('config_') or username.startswith('final_')):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized for enrollment"
        )
    
    return username