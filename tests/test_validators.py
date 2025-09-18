import pytest
from src.validators import validate_cpf, validate_name, validate_age_in_groups, clean_cpf, format_cpf
from src.domain import AgeGroup


class TestCPFValidation:
    """Test CPF validation functions"""

    def test_valid_cpf(self):
        """Test valid CPF numbers"""
        valid_cpfs = [
            "11144477735",
            "12345678909",
            "98765432100"
        ]
        
        for cpf in valid_cpfs:
            assert validate_cpf(cpf), f"CPF {cpf} should be valid"

    def test_invalid_cpf_all_same_digits(self):
        """Test CPF with all same digits"""
        invalid_cpfs = [
            "11111111111",
            "22222222222",
            "00000000000"
        ]
        
        for cpf in invalid_cpfs:
            assert not validate_cpf(cpf), f"CPF {cpf} should be invalid"

    def test_invalid_cpf_wrong_length(self):
        """Test CPF with wrong length"""
        invalid_cpfs = [
            "123456789",      # Too short
            "123456789012",   # Too long
            ""                # Empty
        ]
        
        for cpf in invalid_cpfs:
            assert not validate_cpf(cpf), f"CPF {cpf} should be invalid"

    def test_invalid_cpf_wrong_check_digits(self):
        """Test CPF with wrong check digits"""
        invalid_cpfs = [
            "12345678901",    # Wrong check digits
            "11144477736",    # Wrong second check digit
        ]
        
        for cpf in invalid_cpfs:
            assert not validate_cpf(cpf), f"CPF {cpf} should be invalid"

    def test_clean_cpf(self):
        """Test CPF cleaning function"""
        assert clean_cpf("111.444.777-35") == "11144477735"
        assert clean_cpf("111 444 777 35") == "11144477735"
        assert clean_cpf("111.444.777-35") == "11144477735"
        assert clean_cpf("11144477735") == "11144477735"

    def test_format_cpf(self):
        """Test CPF formatting function"""
        assert format_cpf("11144477735") == "111.444.777-35"
        assert format_cpf("111.444.777-35") == "111.444.777-35"
        assert format_cpf("123") == "123"  # Invalid length, no formatting


class TestNameValidation:
    """Test name validation functions"""

    def test_valid_names(self):
        """Test valid names"""
        valid_names = [
            "João Silva",
            "Maria da Silva Santos",
            "José Carlos de Oliveira",
            "Ana Beatriz",
            "Francisco Xavier"
        ]
        
        for name in valid_names:
            assert validate_name(name), f"Name '{name}' should be valid"

    def test_invalid_single_name(self):
        """Test invalid single names"""
        invalid_names = [
            "João",           # Only first name
            "Silva",          # Only last name
            "",               # Empty
            "   ",            # Only whitespace
        ]
        
        for name in invalid_names:
            assert not validate_name(name), f"Name '{name}' should be invalid"

    def test_invalid_short_names(self):
        """Test names with parts too short"""
        invalid_names = [
            "A B",            # Both parts too short
            "João A",         # Last name too short
            "A Silva",        # First name too short
        ]
        
        for name in invalid_names:
            assert not validate_name(name), f"Name '{name}' should be invalid"

    def test_invalid_names_with_numbers(self):
        """Test names containing numbers or special characters"""
        invalid_names = [
            "João Silva123",
            "Maria@Silva",
            "José-Carlos",
            "Ana_Beatriz"
        ]
        
        for name in invalid_names:
            assert not validate_name(name), f"Name '{name}' should be invalid"

    def test_valid_names_with_accents(self):
        """Test names with accents and special characters"""
        valid_names = [
            "José da Silva",
            "María Santos",
            "João de Souza",
            "Ângela Ribeiro"
        ]
        
        for name in valid_names:
            assert validate_name(name), f"Name '{name}' should be valid"


class TestAgeGroupValidation:
    """Test age group validation functions"""

    def test_age_in_single_group(self):
        """Test age validation with single age group"""
        age_group = AgeGroup(name="Adults", min_age=18, max_age=65)
        age_groups = [age_group]
        
        # Test valid ages
        valid_ages = [18, 25, 40, 65]
        for age in valid_ages:
            is_valid, message = validate_age_in_groups(age, age_groups)
            assert is_valid, f"Age {age} should be valid for group {age_group.name}"
            assert message == age_group.name

        # Test invalid ages
        invalid_ages = [17, 66, 10, 80]
        for age in invalid_ages:
            is_valid, message = validate_age_in_groups(age, age_groups)
            assert not is_valid, f"Age {age} should be invalid for group {age_group.name}"
            assert f"Age {age}" in message

    def test_age_in_multiple_groups(self):
        """Test age validation with multiple age groups"""
        age_groups = [
            AgeGroup(name="Children", min_age=0, max_age=12),
            AgeGroup(name="Teenagers", min_age=13, max_age=17),
            AgeGroup(name="Adults", min_age=18, max_age=65),
            AgeGroup(name="Seniors", min_age=66, max_age=120)
        ]
        
        test_cases = [
            (5, True, "Children"),
            (15, True, "Teenagers"),
            (30, True, "Adults"),
            (70, True, "Seniors"),
            (0, True, "Children"),
            (120, True, "Seniors")
        ]
        
        for age, should_be_valid, expected_group in test_cases:
            is_valid, message = validate_age_in_groups(age, age_groups)
            assert is_valid == should_be_valid, f"Age {age} validation failed"
            if should_be_valid:
                assert message == expected_group, f"Age {age} should be in group {expected_group}"

    def test_age_with_no_groups(self):
        """Test age validation with no age groups configured"""
        is_valid, message = validate_age_in_groups(25, [])
        assert not is_valid
        assert "No age groups configured" in message

    def test_age_gap_between_groups(self):
        """Test age validation with gaps between groups"""
        age_groups = [
            AgeGroup(name="Children", min_age=0, max_age=12),
            AgeGroup(name="Adults", min_age=18, max_age=65)  # Gap: 13-17
        ]
        
        # Test age in gap
        is_valid, message = validate_age_in_groups(15, age_groups)
        assert not is_valid
        assert "Age 15" in message
        assert "Children" in message
        assert "Adults" in message

    def test_age_too_high_for_all_groups(self):
        """Test age higher than all available groups"""
        age_groups = [
            AgeGroup(name="Adults", min_age=18, max_age=65)
        ]
        
        is_valid, message = validate_age_in_groups(80, age_groups)
        assert not is_valid
        assert "too high" in message
        assert "65" in message

    def test_age_too_low_for_all_groups(self):
        """Test age lower than all available groups"""
        age_groups = [
            AgeGroup(name="Adults", min_age=18, max_age=65)
        ]
        
        is_valid, message = validate_age_in_groups(10, age_groups)
        assert not is_valid
        assert "too low" in message
        assert "18" in message


class TestAgeGroupDomainLogic:
    """Test age group domain logic"""

    def test_age_group_contains_age(self):
        """Test age group contains_age method"""
        age_group = AgeGroup(name="Adults", min_age=18, max_age=65)
        
        # Test boundary values
        assert age_group.contains_age(18)  # Min age
        assert age_group.contains_age(65)  # Max age
        assert age_group.contains_age(40)  # Middle age
        
        # Test outside boundaries
        assert not age_group.contains_age(17)  # Below min
        assert not age_group.contains_age(66)  # Above max

    def test_age_group_update(self):
        """Test age group update functionality"""
        age_group = AgeGroup(name="Original", min_age=18, max_age=65)
        original_created_at = age_group.created_at
        
        # Update all fields
        age_group.update(name="Updated", min_age=20, max_age=70)
        
        assert age_group.name == "Updated"
        assert age_group.min_age == 20
        assert age_group.max_age == 70
        assert age_group.updated_at is not None
        assert age_group.created_at == original_created_at  # Should not change

    def test_age_group_partial_update(self):
        """Test age group partial update"""
        age_group = AgeGroup(name="Original", min_age=18, max_age=65)
        
        # Update only name
        age_group.update(name="Updated Name")
        
        assert age_group.name == "Updated Name"
        assert age_group.min_age == 18  # Should remain unchanged
        assert age_group.max_age == 65  # Should remain unchanged