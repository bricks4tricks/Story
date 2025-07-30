import re

PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+])[A-Za-z\d!@#$%^&*()_+]{8,}$"
)
PASSWORD_REQUIREMENTS_MESSAGE = (
    "Password must be at least 8 characters long and include at least one "
    "uppercase letter, one lowercase letter, one number, and one special "
    "character (!@#$%^&*()_+)."
)

def validate_password(password):
    if not PASSWORD_REGEX.fullmatch(password):
        return False, PASSWORD_REQUIREMENTS_MESSAGE
    return True, None
