"""Validator and Assertion Utility"""

import logging

import requests

logger = logging.getLogger(__name__)


def _assert_with_log(condition: bool, message: str):
    """Assert with logging for pass/fail."""
    try:
        assert condition, message  # nosec
        logger.info("Assertion Pass: %s", message)
    except AssertionError:
        logger.error("Assertion Fail: %s", message)
        raise


def assert_true(value: bool, message: str = None):
    """Assert that value is True."""
    if not message:
        message = f"Expected: True Actual: {value}"
    _assert_with_log(value is True, message)


def assert_equals(actual, expected, message: str = None):
    """Assert that actual == expected."""
    if not message:
        message = f"Expected: {expected} Actual: {actual}"
    _assert_with_log(actual == expected, message)


def validate_status_code(response: requests.Response, expected_status_code: int):
    """Assert that response.status_code == expected_status_code."""
    _assert_with_log(
        response.status_code == expected_status_code,
        f"StatusCode => Expected: {expected_status_code} Actual: {response.status_code}",
    )


def validate_response_book(response: requests.Response, expected_book: dict):
    """Validate a single book response matches the expected book."""
    res_json = response.json()
    _assert_with_log(res_json.get("id") is not None, "Book ID should be auto generated")
    _assert_with_log(
        res_json.get("author") == expected_book.get("author"), "Book Author Name"
    )
    _assert_with_log(res_json.get("title") == expected_book.get("title"), "Book Title")


def validate_error_message(response: requests.Response, message: str):
    """Validate the error message in the response."""
    _assert_with_log(
        response.json().get("error") == message,
        f"Error Message: Expected '{message}' Actual '{response.json().get('error')}'",
    )
