import pytest
import os
import boto3
from moto import mock_dynamodb
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import tempfile

# Set test environment variables
os.environ["AGE_GROUPS_TABLE"] = "test-age-groups"
os.environ["ENROLLMENTS_TABLE"] = "test-enrollments"
os.environ["ENV"] = "test"

@pytest.fixture(scope="session")
def mock_aws():
    """Mock AWS services for testing"""
    with mock_dynamodb():
        yield

@pytest.fixture
def dynamodb_tables(mock_aws):
    """Create test DynamoDB tables"""
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    
    # Create age groups table
    age_groups_table = dynamodb.create_table(
        TableName="test-age-groups",
        KeySchema=[
            {"AttributeName": "id", "KeyType": "HASH"}
        ],
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"}
        ],
        BillingMode="PAY_PER_REQUEST"
    )
    
    # Create enrollments table
    enrollments_table = dynamodb.create_table(
        TableName="test-enrollments",
        KeySchema=[
            {"AttributeName": "cpf", "KeyType": "HASH"}
        ],
        AttributeDefinitions=[
            {"AttributeName": "cpf", "AttributeType": "S"}
        ],
        BillingMode="PAY_PER_REQUEST"
    )
    
    return age_groups_table, enrollments_table

@pytest.fixture
def test_auth_file():
    """Create temporary auth file for testing"""
    auth_content = """# Test authentication file
config_admin:admin123
config_user:user456
final_user1:password1
final_user2:password2"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(auth_content)
        temp_file_path = f.name
    
    # Patch the auth file path
    with patch('src.auth.os.path.join', return_value=temp_file_path):
        yield temp_file_path
    
    # Cleanup
    os.unlink(temp_file_path)

@pytest.fixture
def client(dynamodb_tables, test_auth_file):
    """Create test client with mocked dependencies"""
    from src.main import app
    
    # Mock SQS client
    with patch('src.main.sqs') as mock_sqs:
        mock_sqs.send_message.return_value = {"MessageId": "test-message-id"}
        
        with TestClient(app) as test_client:
            yield test_client

@pytest.fixture
def config_auth():
    """Basic auth for configuration user"""
    return ("config_admin", "admin123")

@pytest.fixture
def final_auth():
    """Basic auth for final user"""
    return ("final_user1", "password1")

@pytest.fixture
def invalid_auth():
    """Invalid auth credentials"""
    return ("invalid_user", "invalid_pass")

@pytest.fixture
def sample_age_group():
    """Sample age group data"""
    return {
        "name": "Adults",
        "min_age": 18,
        "max_age": 65
    }

@pytest.fixture
def sample_enrollment():
    """Sample enrollment data"""
    return {
        "name": "João Silva Santos",
        "age": 25,
        "cpf": "11144477735"  # Valid CPF
    }