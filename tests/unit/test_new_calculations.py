import pytest
import uuid
from app.models.calculation import (
    Calculation,
    Exponentiation,
    Modulus,
    Minimum,
    Maximum,
    Average,
)

# Helper function to create a dummy user_id for testing.
def dummy_user_id():
    return uuid.uuid4()

def test_exponentiation_get_result():
    """
    Test that Exponentiation.get_result returns the correct power.
    """
    inputs = [2, 3]
    exponentiation = Exponentiation(user_id=dummy_user_id(), inputs=inputs)
    result = exponentiation.get_result()
    assert result == 8, f"Expected 8, got {result}"

def test_exponentiation_multiple_values():
    """
    Test exponentiation with multiple values (left to right).
    """
    inputs = [2, 3, 2]
    exponentiation = Exponentiation(user_id=dummy_user_id(), inputs=inputs)
    # (2 ** 3) ** 2 = 8 ** 2 = 64
    result = exponentiation.get_result()
    assert result == 64, f"Expected 64, got {result}"

def test_exponentiation_with_decimal():
    """
    Test exponentiation with decimal values.
    """
    inputs = [5, 2]
    exponentiation = Exponentiation(user_id=dummy_user_id(), inputs=inputs)
    result = exponentiation.get_result()
    assert result == 25, f"Expected 25, got {result}"

def test_exponentiation_with_zero():
    """
    Test exponentiation with zero as exponent.
    """
    inputs = [10, 0]
    exponentiation = Exponentiation(user_id=dummy_user_id(), inputs=inputs)
    result = exponentiation.get_result()
    assert result == 1, f"Expected 1, got {result}"

def test_exponentiation_with_negative():
    """
    Test exponentiation with negative exponent.
    """
    inputs = [2, -2]
    exponentiation = Exponentiation(user_id=dummy_user_id(), inputs=inputs)
    result = exponentiation.get_result()
    assert result == 0.25, f"Expected 0.25, got {result}"

def test_exponentiation_invalid_inputs_not_list():
    """
    Test that providing non-list inputs raises ValueError.
    """
    exponentiation = Exponentiation(user_id=dummy_user_id(), inputs="not-a-list")
    with pytest.raises(ValueError, match="Inputs must be a list of numbers."):
        exponentiation.get_result()

def test_exponentiation_invalid_inputs_single_value():
    """
    Test that providing single value raises ValueError.
    """
    exponentiation = Exponentiation(user_id=dummy_user_id(), inputs=[5])
    with pytest.raises(ValueError, match="Inputs must be a list with at least two numbers."):
        exponentiation.get_result()

def test_modulus_get_result():
    """
    Test that Modulus.get_result returns the correct remainder.
    """
    inputs = [10, 3]
    modulus = Modulus(user_id=dummy_user_id(), inputs=inputs)
    result = modulus.get_result()
    assert result == 1, f"Expected 1, got {result}"

def test_modulus_multiple_values():
    """
    Test modulus with multiple values (left to right).
    """
    inputs = [100, 30, 7]
    modulus = Modulus(user_id=dummy_user_id(), inputs=inputs)
    # (100 % 30) % 7 = 10 % 7 = 3
    result = modulus.get_result()
    assert result == 3, f"Expected 3, got {result}"

def test_modulus_exact_division():
    """
    Test modulus when numbers divide evenly.
    """
    inputs = [20, 5]
    modulus = Modulus(user_id=dummy_user_id(), inputs=inputs)
    result = modulus.get_result()
    assert result == 0, f"Expected 0, got {result}"

def test_modulus_with_decimal():
    """
    Test modulus with decimal values.
    """
    inputs = [17.5, 5]
    modulus = Modulus(user_id=dummy_user_id(), inputs=inputs)
    result = modulus.get_result()
    assert result == 2.5, f"Expected 2.5, got {result}"

def test_modulus_by_zero():
    """
    Test that Modulus.get_result raises ValueError when performing modulus by zero.
    """
    inputs = [50, 0]
    modulus = Modulus(user_id=dummy_user_id(), inputs=inputs)
    with pytest.raises(ValueError, match="Cannot perform modulus by zero."):
        modulus.get_result()

def test_modulus_by_zero_in_sequence():
    """
    Test that Modulus raises ValueError when zero appears in middle of sequence.
    """
    inputs = [100, 30, 0]
    modulus = Modulus(user_id=dummy_user_id(), inputs=inputs)
    with pytest.raises(ValueError, match="Cannot perform modulus by zero."):
        modulus.get_result()

def test_modulus_invalid_inputs_not_list():
    """
    Test that providing non-list inputs raises ValueError.
    """
    modulus = Modulus(user_id=dummy_user_id(), inputs="not-a-list")
    with pytest.raises(ValueError, match="Inputs must be a list of numbers."):
        modulus.get_result()

def test_modulus_invalid_inputs_single_value():
    """
    Test that providing single value raises ValueError.
    """
    modulus = Modulus(user_id=dummy_user_id(), inputs=[10])
    with pytest.raises(ValueError, match="Inputs must be a list with at least two numbers."):
        modulus.get_result()

def test_calculation_factory_exponentiation():
    """
    Test the Calculation.create factory method for exponentiation.
    """
    inputs = [3, 4]
    calc = Calculation.create(
        calculation_type='exponentiation',
        user_id=dummy_user_id(),
        inputs=inputs,
    )
    assert isinstance(calc, Exponentiation), "Factory did not return an Exponentiation instance."
    assert calc.get_result() == 81, "Incorrect exponentiation result."

def test_calculation_factory_modulus():
    """
    Test the Calculation.create factory method for modulus.
    """
    inputs = [17, 5]
    calc = Calculation.create(
        calculation_type='modulus',
        user_id=dummy_user_id(),
        inputs=inputs,
    )
    assert isinstance(calc, Modulus), "Factory did not return a Modulus instance."
    assert calc.get_result() == 2, "Incorrect modulus result."

def test_large_exponentiation():
    """
    Test exponentiation with larger numbers.
    """
    inputs = [10, 3]
    exponentiation = Exponentiation(user_id=dummy_user_id(), inputs=inputs)
    result = exponentiation.get_result()
    assert result == 1000, f"Expected 1000, got {result}"

def test_fractional_exponentiation():
    """
    Test exponentiation with fractional exponent (square root).
    """
    inputs = [16, 0.5]
    exponentiation = Exponentiation(user_id=dummy_user_id(), inputs=inputs)
    result = exponentiation.get_result()
    assert result == 4, f"Expected 4, got {result}"

# ============================================================================
# Minimum Tests
# ============================================================================
def test_minimum_basic():
    """Test basic minimum finding"""
    inputs = [5, 2, 9, 1]
    minimum = Minimum(user_id=dummy_user_id(), inputs=inputs)
    result = minimum.get_result()
    assert result == 1

def test_minimum_negative_numbers():
    """Test minimum with negative numbers"""
    inputs = [10, -5, 3, -2]
    minimum = Minimum(user_id=dummy_user_id(), inputs=inputs)
    result = minimum.get_result()
    assert result == -5

def test_minimum_decimals():
    """Test minimum with decimal numbers"""
    inputs = [7.5, 3.2, 9.1, 2.8]
    minimum = Minimum(user_id=dummy_user_id(), inputs=inputs)
    result = minimum.get_result()
    assert result == 2.8

def test_minimum_two_values():
    """Test minimum with just two values"""
    inputs = [10, 5]
    minimum = Minimum(user_id=dummy_user_id(), inputs=inputs)
    result = minimum.get_result()
    assert result == 5

def test_minimum_invalid_inputs():
    """Test minimum with invalid inputs"""
    minimum = Minimum(user_id=dummy_user_id(), inputs="not-a-list")
    with pytest.raises(ValueError, match="Inputs must be a list"):
        minimum.get_result()

def test_minimum_insufficient_inputs():
    """Test minimum with insufficient inputs"""
    minimum = Minimum(user_id=dummy_user_id(), inputs=[10])
    with pytest.raises(ValueError, match="at least two numbers"):
        minimum.get_result()

# ============================================================================
# Maximum Tests
# ============================================================================
def test_maximum_basic():
    """Test basic maximum finding"""
    inputs = [5, 2, 9, 1]
    maximum = Maximum(user_id=dummy_user_id(), inputs=inputs)
    result = maximum.get_result()
    assert result == 9

def test_maximum_negative_numbers():
    """Test maximum with negative numbers"""
    inputs = [-10, -5, -3, -20]
    maximum = Maximum(user_id=dummy_user_id(), inputs=inputs)
    result = maximum.get_result()
    assert result == -3

def test_maximum_decimals():
    """Test maximum with decimal numbers"""
    inputs = [7.5, 3.2, 9.1, 2.8]
    maximum = Maximum(user_id=dummy_user_id(), inputs=inputs)
    result = maximum.get_result()
    assert result == 9.1

def test_maximum_two_values():
    """Test maximum with just two values"""
    inputs = [10, 5]
    maximum = Maximum(user_id=dummy_user_id(), inputs=inputs)
    result = maximum.get_result()
    assert result == 10

def test_maximum_invalid_inputs():
    """Test maximum with invalid inputs"""
    maximum = Maximum(user_id=dummy_user_id(), inputs="not-a-list")
    with pytest.raises(ValueError, match="Inputs must be a list"):
        maximum.get_result()

def test_maximum_insufficient_inputs():
    """Test maximum with insufficient inputs"""
    maximum = Maximum(user_id=dummy_user_id(), inputs=[10])
    with pytest.raises(ValueError, match="at least two numbers"):
        maximum.get_result()

# ============================================================================
# Average Tests
# ============================================================================
def test_average_basic():
    """Test basic average calculation"""
    inputs = [10, 20, 30]
    average = Average(user_id=dummy_user_id(), inputs=inputs)
    result = average.get_result()
    assert result == 20

def test_average_two_values():
    """Test average with two values"""
    inputs = [5, 15]
    average = Average(user_id=dummy_user_id(), inputs=inputs)
    result = average.get_result()
    assert result == 10

def test_average_negative_numbers():
    """Test average with negative numbers"""
    inputs = [-10, 10, 0]
    average = Average(user_id=dummy_user_id(), inputs=inputs)
    result = average.get_result()
    assert result == 0

def test_average_decimals():
    """Test average with decimal numbers"""
    inputs = [2.5, 3.5, 4.0]
    average = Average(user_id=dummy_user_id(), inputs=inputs)
    result = average.get_result()
    assert abs(result - 3.333333) < 0.001

def test_average_many_values():
    """Test average with many values"""
    inputs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    average = Average(user_id=dummy_user_id(), inputs=inputs)
    result = average.get_result()
    assert result == 5.5

def test_average_invalid_inputs():
    """Test average with invalid inputs"""
    average = Average(user_id=dummy_user_id(), inputs="not-a-list")
    with pytest.raises(ValueError, match="Inputs must be a list"):
        average.get_result()

def test_average_insufficient_inputs():
    """Test average with insufficient inputs"""
    average = Average(user_id=dummy_user_id(), inputs=[10])
    with pytest.raises(ValueError, match="at least two numbers"):
        average.get_result()

# ============================================================================
# Factory Pattern Tests for New Types
# ============================================================================
def test_factory_minimum():
    """Test factory creates Minimum instance"""
    calc = Calculation.create('minimum', dummy_user_id(), [5, 2, 9, 1])
    assert isinstance(calc, Minimum)
    assert calc.get_result() == 1

def test_factory_maximum():
    """Test factory creates Maximum instance"""
    calc = Calculation.create('maximum', dummy_user_id(), [5, 2, 9, 1])
    assert isinstance(calc, Maximum)
    assert calc.get_result() == 9

def test_factory_average():
    """Test factory creates Average instance"""
    calc = Calculation.create('average', dummy_user_id(), [10, 20, 30])
    assert isinstance(calc, Average)
    assert calc.get_result() == 20
