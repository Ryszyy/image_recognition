class InvalidDataProvided(Exception):
    """Raised when user already exist"""
    status_code = 300

    def __str__(self):
        return "Invalid Data Provided"


class UserAlreadyExist(Exception):
    """Raised when user already exist"""
    status_code = 301

    def __str__(self):
        return "User Already Exist"


class WeakPassword(Exception):
    """Raised when password is weak"""
    status_code = 302

    def __str__(self):
        return "Weak Password"


class UserDoesNotExist(Exception):
    """Raised when user does not exist"""
    status_code = 304

    def __str__(self):
        return "User Does Not Exist"


class WrongPassword(Exception):
    """Raised when password is wrong"""
    status_code = 305

    def __str__(self):
        return "Wrong Password"


class NotEnoughTokens(Exception):
    """Raised when not enough tokens"""
    status_code = 306

    def __str__(self):
        return "Not Enough Tokens"
