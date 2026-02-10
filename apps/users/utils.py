"""
Utility functions for user management.
"""

import secrets
import string


def generate_secure_password(length=12):
    """
    Generate a secure random password.

    Args:
        length (int): Length of password (default: 12)

    Returns:
        str: Randomly generated password

    The password contains:
    - Uppercase letters
    - Lowercase letters
    - Digits
    - Special characters
    """
    # Define character sets
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special = '!@#$%^&*'

    # Ensure at least one character from each set
    password = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(special),
    ]

    # Fill the rest with random characters from all sets
    all_characters = uppercase + lowercase + digits + special
    password += [secrets.choice(all_characters) for _ in range(length - 4)]

    # Shuffle to avoid predictable patterns
    secrets.SystemRandom().shuffle(password)

    return ''.join(password)


def generate_invitation_token():
    """
    Generate a secure token for invitation URLs.

    Returns:
        str: URL-safe token (48 characters)
    """
    return secrets.token_urlsafe(48)
