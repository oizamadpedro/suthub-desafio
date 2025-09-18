import pytest
from fastapi import status


class TestIntegrationWorkflows:
    """Test end-to-end integration workflows"""

    def test_complete_age_group_and_enrollment_workflow(self, client, config_auth, final_auth):
        """Test complete workflow: create age groups, then enroll users"""
        
        # Step 1: Config user creates multiple age groups
        age_groups = [
            {"name": "Children", "min_age": 0, "max_age": 12},
            {"name": "Teenagers", "min_age": 13, "max_age": 17},
            {"name": "Young Adults", "min_age": 18, "max_age": 30},
            {"name": "Adults", "min_age": 31, "max_age": 65},
            {"name": "Seniors", "min_age": 66, "max_age": 120}
        ]
        
        created_groups = []
        for group_data in age_groups:
            response = client.post("/config/age-groups", json=group_data, auth=config_auth)
            assert response.status_code == status.HTTP_201_CREATED
            created_groups.append(response.json())
        
        # Step 2: Verify all groups were created
        list_response = client.get("/config/age-groups", auth=config_auth)
        assert list_response.status_code == status.HTTP_200_OK
        assert len(list_response.json()) == 5
        
        # Step 3: Final users enroll in different age groups
        enrollments = [
            {"name": "Ana Silva Santos", "age": 8, "cpf": "12345678901"},    # Children
            {"name": "Pedro Costa Lima", "age": 15, "cpf": "98765432109"},   # Teenagers
            {"name": "Maria Oliveira Souza", "age": 25, "cpf": "11144477735"}, # Young Adults
            {"name": "João Santos Silva", "age": 45, "cpf": "22233344456"},  # Adults
            {"name": "Rosa Lima Costa", "age": 70, "cpf": "77788899900"}     # Seniors
        ]
        
        created_enrollments = []
        for enrollment_data in enrollments:
            response = client.post("/enroll", json=enrollment_data, auth=final_auth)
            assert response.status_code == status.HTTP_201_CREATED
            created_enrollments.append(response.json())
        
        # Step 4: Verify all enrollments were created and assigned to correct groups
        list_enrollments_response = client.get("/enrollments", auth=final_auth)
        assert list_enrollments_response.status_code == status.HTTP_200_OK
        enrollment_list = list_enrollments_response.json()
        assert len(enrollment_list) == 5
        
        # Verify correct age group assignments
        expected_assignments = {
            "12345678901": "Children",
            "98765432109": "Teenagers", 
            "11144477735": "Young Adults",
            "22233344456": "Adults",
            "77788899900": "Seniors"
        }
        
        for enrollment in enrollment_list:
            cpf = enrollment["cpf"]
            expected_group = expected_assignments[cpf]
            assert enrollment["age_group"] == expected_group
        
        # Step 5: Test individual enrollment retrieval
        for cpf in expected_assignments.keys():
            response = client.get(f"/enrollments/{cpf}", auth=final_auth)
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["cpf"] == cpf

    def test_age_group_modification_impact_on_enrollments(self, client, config_auth, final_auth):
        """Test how age group modifications impact existing enrollments"""
        
        # Create age group
        age_group_data = {"name": "Adults", "min_age": 18, "max_age": 65}
        create_response = client.post("/config/age-groups", json=age_group_data, auth=config_auth)
        group_id = create_response.json()["id"]
        
        # Create enrollment
        enrollment_data = {"name": "João Silva Santos", "age": 25, "cpf": "11144477735"}
        enroll_response = client.post("/enroll", json=enrollment_data, auth=final_auth)
        assert enroll_response.status_code == status.HTTP_201_CREATED
        assert enroll_response.json()["age_group"] == "Adults"
        
        # Modify age group name
        update_data = {"name": "Working Adults"}
        update_response = client.put(f"/config/age-groups/{group_id}", json=update_data, auth=config_auth)
        assert update_response.status_code == status.HTTP_200_OK
        
        # Note: In a real system, you might want to update existing enrollments
        # when age group names change. This test demonstrates the current behavior.
        enrollment_check = client.get(f"/enrollments/{enrollment_data['cpf']}", auth=final_auth)
        assert enrollment_check.status_code == status.HTTP_200_OK

    def test_enrollment_error_handling_workflow(self, client, config_auth, final_auth):
        """Test error handling in enrollment workflow"""
        
        # Try to enroll without any age groups
        enrollment_data = {"name": "João Silva Santos", "age": 25, "cpf": "11144477735"}
        response = client.post("/enroll", json=enrollment_data, auth=final_auth)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No age group found" in response.json()["detail"]
        
        # Create age group for specific range
        age_group_data = {"name": "Adults", "min_age": 30, "max_age": 50}
        client.post("/config/age-groups", json=age_group_data, auth=config_auth)
        
        # Try to enroll someone outside the range
        young_person = {"name": "Ana Silva Santos", "age": 20, "cpf": "12345678901"}
        response = client.post("/enroll", json=young_person, auth=final_auth)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Try to enroll someone within the range
        adult_person = {"name": "Carlos Silva Santos", "age": 35, "cpf": "11144477735"}
        response = client.post("/enroll", json=adult_person, auth=final_auth)
        assert response.status_code == status.HTTP_201_CREATED

    def test_concurrent_age_group_operations(self, client, config_auth):
        """Test concurrent age group operations"""
        
        # Create first age group
        group1_data = {"name": "Group1", "min_age": 0, "max_age": 20}
        response1 = client.post("/config/age-groups", json=group1_data, auth=config_auth)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Try to create overlapping age group
        group2_data = {"name": "Group2", "min_age": 15, "max_age": 35}
        response2 = client.post("/config/age-groups", json=group2_data, auth=config_auth)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "overlaps" in response2.json()["detail"]
        
        # Create non-overlapping age group
        group3_data = {"name": "Group3", "min_age": 21, "max_age": 40}
        response3 = client.post("/config/age-groups", json=group3_data, auth=config_auth)
        assert response3.status_code == status.HTTP_201_CREATED

    def test_user_permission_boundaries(self, client, config_auth, final_auth):
        """Test user permission boundaries across different operations"""
        
        # Config user can create age groups
        age_group_data = {"name": "Test Group", "min_age": 18, "max_age": 65}
        response = client.post("/config/age-groups", json=age_group_data, auth=config_auth)
        assert response.status_code == status.HTTP_201_CREATED
        group_id = response.json()["id"]
        
        # Final user cannot access config endpoints
        response = client.get("/config/age-groups", auth=final_auth)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        response = client.get(f"/config/age-groups/{group_id}", auth=final_auth)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        response = client.put(f"/config/age-groups/{group_id}", json={"name": "Updated"}, auth=final_auth)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        response = client.delete(f"/config/age-groups/{group_id}", auth=final_auth)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Both users can access enrollment endpoints
        enrollment_data = {"name": "Test User Name", "age": 25, "cpf": "11144477735"}
        
        # Final user can enroll
        response = client.post("/enroll", json=enrollment_data, auth=final_auth)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Both can list enrollments
        response = client.get("/enrollments", auth=final_auth)
        assert response.status_code == status.HTTP_200_OK
        
        response = client.get("/enrollments", auth=config_auth)
        assert response.status_code == status.HTTP_200_OK

    def test_data_consistency_workflow(self, client, config_auth, final_auth):
        """Test data consistency across operations"""
        
        # Create age groups with specific configuration
        groups = [
            {"name": "Young", "min_age": 18, "max_age": 30},
            {"name": "Middle", "min_age": 31, "max_age": 50},
            {"name": "Senior", "min_age": 51, "max_age": 80}
        ]
        
        group_ids = []
        for group_data in groups:
            response = client.post("/config/age-groups", json=group_data, auth=config_auth)
            group_ids.append(response.json()["id"])
        
        # Create enrollments for each group
        enrollments = [
            {"name": "Young Person Name", "age": 25, "cpf": "11111111111"},
            {"name": "Middle Person Name", "age": 40, "cpf": "22222222222"},
            {"name": "Senior Person Name", "age": 60, "cpf": "33333333333"}
        ]
        
        for enrollment_data in enrollments:
            response = client.post("/enroll", json=enrollment_data, auth=final_auth)
            assert response.status_code == status.HTTP_201_CREATED
        
        # Verify data consistency
        enrollment_list = client.get("/enrollments", auth=final_auth).json()
        assert len(enrollment_list) == 3
        
        # Verify each enrollment is in correct group
        age_group_mapping = {25: "Young", 40: "Middle", 60: "Senior"}
        for enrollment in enrollment_list:
            expected_group = age_group_mapping[enrollment["age"]]
            assert enrollment["age_group"] == expected_group
        
        # Delete one age group and verify we can't enroll in that range anymore
        # Note: In production, you might want to handle existing enrollments
        response = client.delete(f"/config/age-groups/{group_ids[0]}", auth=config_auth)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Try to enroll new person in deleted age range
        new_young_person = {"name": "Another Young Person", "age": 28, "cpf": "44444444444"}
        response = client.post("/enroll", json=new_young_person, auth=final_auth)
        assert response.status_code == status.HTTP_400_BAD_REQUEST