import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import (
    validate_email,
    validate_password,
    EMAIL_REQUIREMENTS_MESSAGE,
    PASSWORD_REQUIREMENTS_MESSAGE,
)


def test_validate_email_success():
    assert validate_email("user@example.com") == (True, None)


def test_validate_email_failure():
    assert validate_email("userexample.com") == (False, EMAIL_REQUIREMENTS_MESSAGE)


def test_validate_email_with_spaces_fails():
    """Emails containing whitespace should be rejected."""
    assert validate_email("user name@example.com") == (
        False,
        EMAIL_REQUIREMENTS_MESSAGE,
    )


def test_validate_email_none_input():
    """`None` should be treated as an invalid email rather than raising."""
    assert validate_email(None) == (False, EMAIL_REQUIREMENTS_MESSAGE)


def test_validate_password_success():
    assert validate_password("StrongPass1!") == (True, None)


def test_validate_password_failure():
    valid, msg = validate_password("weakpass")
    assert not valid
    assert msg == PASSWORD_REQUIREMENTS_MESSAGE


def test_validate_password_none_input():
    """`None` passwords should be rejected without raising."""
    assert validate_password(None) == (False, PASSWORD_REQUIREMENTS_MESSAGE)
