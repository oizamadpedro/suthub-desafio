import pytest
from fastapi import status


class TestAgeGroupsEndpoints:
    """Test Configuration User endpoints for age groups management"""

    def test_create_age_group_success(self, client, config_auth, sample_age_group):
        """Test successful age group creation"""
        response = client.post("/config/age-groups", json=sample_age_group, auth=config_auth)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == sample_age_group["name"]
        assert data["min_age"] == sample_age_group["min_age"]
        assert data["max_age"] == sample_age_group["max_age"]
        assert "id" in data
        assert "created_at" in data

    def test_create_age_group_invalid_range(self, client, config_auth):
        """Test age group creation with invalid range (max < min)"""
        invalid_group = {"name": "Invalid", "min_age": 25, "max_age": 18}
        response = client.post("/config/age-groups", json=invalid_group, auth=config_auth)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_overlapping_age_groups(self, client, config_auth):
        """Test creation of overlapping age groups should fail"""
        # Create first age group
        first_group = {"name": "Young Adults", "min_age": 18, "max_age": 30}
        response1 = client.post("/config/age-groups", json=first_group, auth=config_auth)
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create overlapping age group
        overlapping_group = {"name": "Adults", "min_age": 25, "max_age": 40}
        response2 = client.post("/config/age-groups", json=overlapping_group, auth=config_auth)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "overlaps" in response2.json()["detail"]

    def test_list_age_groups_empty(self, client, config_auth):
        """Test listing age groups when none exist"""
        response = client.get("/config/age-groups", auth=config_auth)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_age_groups_with_data(self, client, config_auth, sample_age_group):
        """Test listing age groups with existing data"""
        # Create an age group first
        create_response = client.post("/config/age-groups", json=sample_age_group, auth=config_auth)
        created_id = create_response.json()["id"]
        
        # List age groups
        response = client.get("/config/age-groups", auth=config_auth)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == created_id

    def test_get_age_group_by_id(self, client, config_auth, sample_age_group):
        """Test getting specific age group by ID"""
        # Create an age group first
        create_response = client.post("/config/age-groups", json=sample_age_group, auth=config_auth)
        created_id = create_response.json()["id"]
        
        # Get the age group
        response = client.get(f"/config/age-groups/{created_id}", auth=config_auth)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == created_id
        assert data["name"] == sample_age_group["name"]

    def test_get_nonexistent_age_group(self, client, config_auth):
        """Test getting nonexistent age group returns 404"""
        response = client.get("/config/age-groups/nonexistent-id", auth=config_auth)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_age_group(self, client, config_auth, sample_age_group):
        """Test updating age group"""
        # Create an age group first
        create_response = client.post("/config/age-groups", json=sample_age_group, auth=config_auth)
        created_id = create_response.json()["id"]
        
        # Update the age group
        update_data = {"name": "Updated Adults", "min_age": 20, "max_age": 70}
        response = client.put(f"/config/age-groups/{created_id}", json=update_data, auth=config_auth)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Adults"
        assert data["min_age"] == 20
        assert data["max_age"] == 70
        assert data["updated_at"] is not None

    def test_update_nonexistent_age_group(self, client, config_auth):
        """Test updating nonexistent age group returns 404"""
        update_data = {"name": "Updated"}
        response = client.put("/config/age-groups/nonexistent-id", json=update_data, auth=config_auth)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_partial_update_age_group(self, client, config_auth, sample_age_group):
        """Test partial update of age group"""
        # Create an age group first
        create_response = client.post("/config/age-groups", json=sample_age_group, auth=config_auth)
        created_id = create_response.json()["id"]
        
        # Partial update (only name)
        update_data = {"name": "Partially Updated"}
        response = client.put(f"/config/age-groups/{created_id}", json=update_data, auth=config_auth)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Partially Updated"
        # Original ages should remain
        assert data["min_age"] == sample_age_group["min_age"]
        assert data["max_age"] == sample_age_group["max_age"]

    def test_delete_age_group(self, client, config_auth, sample_age_group):
        """Test deleting age group"""
        # Create an age group first
        create_response = client.post("/config/age-groups", json=sample_age_group, auth=config_auth)
        created_id = create_response.json()["id"]
        
        # Delete the age group
        response = client.delete(f"/config/age-groups/{created_id}", auth=config_auth)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it's deleted
        get_response = client.get(f"/config/age-groups/{created_id}", auth=config_auth)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_age_group(self, client, config_auth):
        """Test deleting nonexistent age group returns 404"""
        response = client.delete("/config/age-groups/nonexistent-id", auth=config_auth)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_age_group_with_boundary_values(self, client, config_auth):
        """Test age group creation with boundary values"""
        boundary_group = {"name": "Full Range", "min_age": 0, "max_age": 120}
        response = client.post("/config/age-groups", json=boundary_group, auth=config_auth)
        
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_age_group_invalid_ages(self, client, config_auth):
        """Test age group creation with invalid age values"""
        # Negative age
        invalid_group1 = {"name": "Invalid", "min_age": -1, "max_age": 10}
        response1 = client.post("/config/age-groups", json=invalid_group1, auth=config_auth)
        assert response1.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Age over 120
        invalid_group2 = {"name": "Invalid", "min_age": 0, "max_age": 130}
        response2 = client.post("/config/age-groups", json=invalid_group2, auth=config_auth)
        assert response2.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY