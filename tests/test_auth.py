import pytest
from fastapi import status


class TestAuthentication:
    """Test authentication and authorization"""

    def test_hello_endpoint_no_auth(self, client):
        """Test that hello endpoint doesn't require auth"""
        response = client.get("/hello")
        assert response.status_code == status.HTTP_200_OK
        assert "Hello World" in response.json()["message"]

    def test_config_endpoint_without_auth(self, client):
        """Test that config endpoints require authentication"""
        response = client.get("/config/age-groups")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_enroll_endpoint_without_auth(self, client, sample_enrollment):
        """Test that enrollment endpoints require authentication"""
        response = client.post("/enroll", json=sample_enrollment)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_config_user_can_access_config_endpoints(self, client, config_auth):
        """Test that config user can access config endpoints"""
        response = client.get("/config/age-groups", auth=config_auth)
        assert response.status_code == status.HTTP_200_OK

    def test_final_user_cannot_access_config_endpoints(self, client, final_auth):
        """Test that final user cannot access config endpoints"""
        response = client.get("/config/age-groups", auth=final_auth)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_config_user_can_enroll(self, client, config_auth, sample_enrollment):
        """Test that config user can perform enrollment"""
        # First create an age group
        age_group_data = {"name": "Adults", "min_age": 18, "max_age": 65}
        client.post("/config/age-groups", json=age_group_data, auth=config_auth)
        
        # Then try to enroll
        response = client.post("/enroll", json=sample_enrollment, auth=config_auth)
        assert response.status_code == status.HTTP_201_CREATED

    def test_final_user_can_enroll(self, client, final_auth, config_auth, sample_enrollment):
        """Test that final user can perform enrollment"""
        # First create an age group using config user
        age_group_data = {"name": "Adults", "min_age": 18, "max_age": 65}
        client.post("/config/age-groups", json=age_group_data, auth=config_auth)
        
        # Then try to enroll with final user
        response = client.post("/enroll", json=sample_enrollment, auth=final_auth)
        assert response.status_code == status.HTTP_201_CREATED

    def test_invalid_credentials(self, client, invalid_auth):
        """Test invalid credentials are rejected"""
        response = client.get("/config/age-groups", auth=invalid_auth)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_wrong_user_type_for_config(self, client, final_auth):
        """Test that final user cannot access config endpoints"""
        response = client.post("/config/age-groups", json={"name": "Test", "min_age": 0, "max_age": 10}, auth=final_auth)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Configuration privileges required" in response.json()["detail"]