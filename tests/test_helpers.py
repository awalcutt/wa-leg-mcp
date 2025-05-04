"""
Helper functions for tests to reduce duplication and create reusable test patterns.
"""

from unittest.mock import patch


def assert_api_error_handling(function_under_test, mock_client_method, error_message, **kwargs):
    """
    Test error handling for API calls.

    This helper function tests that a function properly handles API errors
    by checking that it returns an object with an error key containing
    the expected error message.

    Args:
        function_under_test: The function to test
        mock_client_method: The mocked client method that should raise an exception
        error_message: The expected error message in the result
        **kwargs: Arguments to pass to the function under test

    Returns:
        The result from the function under test
    """
    # Configure the mock to raise an exception
    mock_client_method.side_effect = Exception("API Error")

    # Call the function
    result = function_under_test(**kwargs)

    # Verify error handling
    assert "error" in result
    assert error_message in result["error"]

    return result


def assert_not_found_handling(function_under_test, mock_client_method, error_message, **kwargs):
    """
    Test not found handling for API calls.

    This helper function tests that a function properly handles not found errors
    by checking that it returns an object with an error key containing
    the expected error message.

    Args:
        function_under_test: The function to test
        mock_client_method: The mocked client method that should return None
        error_message: The expected error message in the result
        **kwargs: Arguments to pass to the function under test

    Returns:
        The result from the function under test
    """
    # Configure the mock to return None
    mock_client_method.return_value = None

    # Call the function
    result = function_under_test(**kwargs)

    # Verify error handling
    assert "error" in result
    assert error_message in result["error"]

    return result


def mock_current_biennium(biennium="2023-24"):
    """
    Create a context manager for mocking get_current_biennium.

    Args:
        biennium: The biennium to return from the mock

    Returns:
        A context manager that patches get_current_biennium
    """
    return patch("wa_leg_mcp.tools.bill_tools.get_current_biennium", return_value=biennium)


def mock_current_year(year="2023"):
    """
    Create a context manager for mocking get_current_year.

    Args:
        year: The year to return from the mock

    Returns:
        A context manager that patches get_current_year
    """
    return patch("wa_leg_mcp.tools.bill_tools.get_current_year", return_value=year)


def create_parametrized_test_cases(*cases):
    """
    Create a list of parametrized test cases with descriptions.

    This function takes a list of test cases and returns a list of tuples
    that can be used with pytest.mark.parametrize. Each test case should be
    a tuple of (scenario_name, inputs, expected_outputs).

    Args:
        *cases: Tuples of (scenario_name, inputs, expected_outputs)

    Returns:
        A list of tuples for pytest.mark.parametrize
    """
    return [(case[0], *case[1], *case[2]) for case in cases]


def create_success_error_test_cases(success_case, error_cases):
    """
    Create a list of test cases for success and error scenarios.

    Args:
        success_case: Tuple of (inputs, expected_outputs) for success case
        error_cases: List of tuples of (error_name, inputs, expected_error) for error cases

    Returns:
        A list of tuples for pytest.mark.parametrize
    """
    cases = [("success", *success_case[0], *success_case[1])]
    for error_name, inputs, expected_error in error_cases:
        cases.append((error_name, *inputs, None, expected_error))
    return cases


def patch_module_client(module_path, client_name="wsl_client"):
    """
    Create a context manager for patching a client in a module.

    This helper function creates a context manager that patches a client
    in a module, which is useful for testing functions that use clients.

    Args:
        module_path: The path to the module containing the client
        client_name: The name of the client to patch

    Returns:
        A context manager that patches the client
    """
    return patch(f"{module_path}.{client_name}")


def setup_mock_client_method(mock_client, method_name, return_value=None, side_effect=None):
    """
    Set up a mock client method with the specified return value or side effect.

    Args:
        mock_client: The mock client object
        method_name: The name of the method to mock
        return_value: The value to return from the method
        side_effect: The side effect to use for the method

    Returns:
        The mock method
    """
    mock_method = getattr(mock_client, method_name)
    if side_effect is not None:
        mock_method.side_effect = side_effect
    else:
        mock_method.return_value = return_value
    return mock_method
