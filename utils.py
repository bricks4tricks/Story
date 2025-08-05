import re

# Regex enforcing an '@' symbol followed by a period in the domain portion,
# and disallowing any whitespace characters. Previously the regex
# ``[^@]+@[^@]+\.[^@]+`` allowed spaces in the local part which meant
# emails like ``'user name@example.com'`` were considered valid. The
# updated pattern uses ``\s`` to exclude whitespace characters in all
# sections of the email address.
EMAIL_REGEX = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
EMAIL_REQUIREMENTS_MESSAGE = "Invalid email address"

PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+])[A-Za-z\d!@#$%^&*()_+]{8,}$"
)
PASSWORD_REQUIREMENTS_MESSAGE = (
    "Password must be at least 8 characters long and include at least one "
    "uppercase letter, one lowercase letter, one number, and one special "
    "character (!@#$%^&*()_+)."
)

def validate_password(password):
    """Validate a password against complexity requirements.

    ``re.Pattern.fullmatch`` raises a ``TypeError`` when passed ``None`` or
    a non-string value.  This function is often used with form data where
    values may be missing, so guard against those cases explicitly instead of
    bubbling up an exception.
    """

    if not isinstance(password, str) or not PASSWORD_REGEX.fullmatch(password):
        return False, PASSWORD_REQUIREMENTS_MESSAGE
    return True, None


def validate_email(email):
    """Return ``True`` if *email* appears valid.

    Similar to :func:`validate_password`, ``EMAIL_REGEX.fullmatch`` expects a
    string.  Supplying ``None`` (for example, when the client omits the email
    field) would previously raise ``TypeError``.  Instead, treat any
    non-string input as invalid and return the standard requirements message.
    """

    if not isinstance(email, str) or not EMAIL_REGEX.fullmatch(email):
        return False, EMAIL_REQUIREMENTS_MESSAGE
    return True, None
