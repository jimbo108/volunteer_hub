import logging

_error_dict = {}

EMAIL_INVALID_CODE = 101
EMAIL_INVALID_STRING = "Email invalid"
PASSWORD_INVALID_CODE = 102
PASSWORD_INVALID_STRING = "Password invalid"

_error_dict[EMAIL_INVALID_CODE] = EMAIL_INVALID_STRING
_error_dict[PASSWORD_INVALID_CODE] = PASSWORD_INVALID_STRING

FAILED_TO_COMMIT_USER_CODE = 201
FAILED_TO_COMMIT_USER_STRING = "Failed to commit user to database"
FAILED_TO_QUERY_FOR_USER_CODE = 202
FAILED_TO_QUERY_FOR_USER_STRING = "Failed to query database for user"

_error_dict[FAILED_TO_COMMIT_USER_CODE] = FAILED_TO_COMMIT_USER_STRING
_error_dict[FAILED_TO_QUERY_FOR_USER_CODE] = FAILED_TO_QUERY_FOR_USER_STRING

USER_WITH_EMAIL_ALREADY_EXISTS_CODE = 301
USER_WITH_EMAIL_ALREADY_EXISTS_STRING = "User with that email already exists"

_error_dict[USER_WITH_EMAIL_ALREADY_EXISTS_CODE] = USER_WITH_EMAIL_ALREADY_EXISTS_STRING


def create_response(code):
    if code not in _error_dict:
        logging.error("Called create_response with an invalid error code.")
        raise ValueError("Not a valid code.")

    return {
        'success': False,
        'error_code': code,
        'error_string': _error_dict[code]
    }


def log_error(code):
    if code not in _error_dict:
        logging.error("Called log_error with an invalid error code.")
        raise ValueError("Not a valid code.")

    logging.error(get_error_string(code))


def get_error_string(code):
    if code not in _error_dict:
        logging.error("Called get_error_string with an invalid error code.")
        raise ValueError("Not a valid code.")

    return _error_dict[code]
