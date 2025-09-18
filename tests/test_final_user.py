import pytest
from fastapi import status


class TestEnrollmentEndpoints:
    """Test Final User endpoints for enrollment management"""

    def setup_age_group(self, client, config_auth):
        """Helper method to create an age group for enrollment tests"""
        age_group_data = {"name": "Adults", "min_age": 18, "max_age": 65}
        response = client.post("/config/age-groups", json=age_group_data, auth=config_auth)
        return response.json()["id"]

    def test_create_enrollment_success(self, client, final_auth, config_auth, sample_enrollment):
        """Test successful enrollment creation"""
        # Setup age group first
        self.setup_age_group(client, config_auth)
        
        # Create enrollment
        response = client.post("/enroll", json=sample_enrollment, auth=final_auth)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == sample_enrollment["name"]
        assert data["age"] == sample_enrollment["age"]
        assert data["cpf"] == sample_enrollment["cpf"]
        assert data["age_group"] == "Adults"
        assert "created_at" in data

    def test_create_enrollment_no_age_group(self, client, final_auth, sample_enrollment):
        """Test enrollment creation when no matching age group exists"""
        response = client.post("/enroll", json=sample_enrollment, auth=final_auth)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No age group found" in response.json()["detail"]

    def test_create_enrollment_age_outside_groups(self, client, final_auth, config_auth):
        """Test enrollment with age outside existing groups"""
        # Create age group for adults only
        age_group_data = {"name": "Adults", "min_age": 18, "max_age": 65}
        client.post("/config/age-groups", json=age_group_data, auth=config_auth)
        
        # Try to enroll a child
        child_enrollment = {
            "name": "Maria Silva Santos",
            "age": 10,
            "cpf": "11144477735"
        }
        response = client.post("/enroll", json=child_enrollment, auth=final_auth)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No age group found for age 10" in response.json()["detail"]

    def test_create_enrollment_duplicate_cpf(self, client, final_auth, config_auth, sample_enrollment):
        """Test enrollment creation with duplicate CPF"""
        # Setup age group
        self.setup_age_group(client, config_auth)
        
        # Create first enrollment
        response1 = client.post("/enroll", json=sample_enrollment, auth=final_auth)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Try to create duplicate
        response2 = client.post("/enroll", json=sample_enrollment, auth=final_auth)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "CPF already enrolled" in response2.json()["detail"]

    def test_create_enrollment_invalid_cpf(self, client, final_auth, config_auth):
        """Test enrollment creation with invalid CPF"""
        # Setup age group
        self.setup_age_group(client, config_auth)
        
        invalid_enrollment = {
            "name": "João Silva Santos",
            "age": 25,
            "cpf": "12345678900"  # Invalid CPF
        }
        response = client.post("/enroll", json=invalid_enrollment, auth=final_auth)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_enrollment_invalid_name(self, client, final_auth, config_auth):
        """Test enrollment creation with invalid name"""
        # Setup age group
        self.setup_age_group(client, config_auth)
        
        invalid_enrollment = {
            "name": "João",  # Only first name
            "age": 25,
            "cpf": "11144477735"
        }
        response = client.post("/enroll", json=invalid_enrollment, auth=final_auth)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_enrollments_empty(self, client, final_auth):
        """Test listing enrollments when none exist"""
        response = client.get("/enrollments", auth=final_auth)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_enrollments_with_data(self, client, final_auth, config_auth, sample_enrollment):
        """Test listing enrollments with existing data"""
        # Setup and create enrollment
        self.setup_age_group(client, config_auth)
        create_response = client.post("/enroll", json=sample_enrollment, auth=final_auth)
        
        # List enrollments
        response = client.get("/enrollments", auth=final_auth)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["cpf"] == sample_enrollment["cpf"]

    def test_get_enrollment_by_cpf(self, client, final_auth, config_auth, sample_enrollment):
        """Test getting specific enrollment by CPF"""
        # Setup and create enrollment
        self.setup_age_group(client, config_auth)
        client.post("/enroll", json=sample_enrollment, auth=final_auth)
        
        # Get the enrollment
        response = client.get(f"/enrollments/{sample_enrollment['cpf']}", auth=final_auth)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["cpf"] == sample_enrollment["cpf"]
        assert data["name"] == sample_enrollment["name"]

    def test_get_nonexistent_enrollment(self, client, final_auth):
        """Test getting nonexistent enrollment returns 404"""
        response = client.get("/enrollments/99999999999", auth=final_auth)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_enrollment(self, client, final_auth, config_auth, sample_enrollment):
        """Test deleting enrollment"""
        # Setup and create enrollment
        self.setup_age_group(client, config_auth)
        client.post("/enroll", json=sample_enrollment, auth=final_auth)
        
        # Delete the enrollment
        response = client.delete(f"/enrollments/{sample_enrollment['cpf']}", auth=final_auth)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it's deleted
        get_response = client.get(f"/enrollments/{sample_enrollment['cpf']}", auth=final_auth)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_enrollment(self, client, final_auth):
        """Test deleting nonexistent enrollment returns 404"""
        response = client.delete("/enrollments/99999999999", auth=final_auth)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_enrollment_with_different_age_groups(self, client, final_auth, config_auth):
        """Test enrollments are assigned to correct age groups"""
        # Create multiple age groups
        child_group = {"name": "Children", "min_age": 0, "max_age": 12}
        teen_group = {"name": "Teenagers", "min_age": 13, "max_age": 17}
        adult_group = {"name": "Adults", "min_age": 18, "max_age": 65}
        
        client.post("/config/age-groups", json=child_group, auth=config_auth)
        client.post("/config/age-groups", json=teen_group, auth=config_auth)
        client.post("/config/age-groups", json=adult_group, auth=config_auth)
        
        # Test child enrollment
        child_enrollment = {
            "name": "Ana Silva Santos",
            "age": 8,
            "cpf": "12345678901"
        }
        response1 = client.post("/enroll", json=child_enrollment, auth=final_auth)
        assert response1.status_code == status.HTTP_201_CREATED
        assert response1.json()["age_group"] == "Children"
        
        # Test teen enrollment
        teen_enrollment = {
            "name": "Pedro Silva Santos",
            "age": 15,
            "cpf": "98765432109"
        }
        response2 = client.post("/enroll", json=teen_enrollment, auth=final_auth)
        assert response2.status_code == status.HTTP_201_CREATED
        assert response2.json()["age_group"] == "Teenagers"
        
        # Test adult enrollment
        adult_enrollment = {
            "name": "Carlos Silva Santos",
            "age": 30,
            "cpf": "11144477735"
        }
        response3 = client.post("/enroll", json=adult_enrollment, auth=final_auth)
        assert response3.status_code == status.HTTP_201_CREATED
        assert response3.json()["age_group"] == "Adults"

    def test_config_user_can_manage_enrollments(self, client, config_auth, sample_enrollment):
        """Test that config users can also manage enrollments"""
        # Setup age group
        self.setup_age_group(client, config_auth)
        
        # Config user creates enrollment
        response = client.post("/enroll", json=sample_enrollment, auth=config_auth)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Config user can list enrollments
        list_response = client.get("/enrollments", auth=config_auth)
        assert list_response.status_code == status.HTTP_200_OK
        
        # Config user can delete enrollment
        delete_response = client.delete(f"/enrollments/{sample_enrollment['cpf']}", auth=config_auth)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT