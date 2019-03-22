import logging
from typing import Dict, Any, Union, List
_error_dict = {}

EMAIL_INVALID_CODE = 101
EMAIL_INVALID_STRING = "Email invalid"
PASSWORD_INVALID_CODE = 102
PASSWORD_INVALID_STRING = "Password invalid"
NAME_INVALID_CODE = 103
NAME_INVALID_STRING = "Name invalid"
PHONE_NUMBER_INVALID_CODE = 104
PHONE_NUMBER_INVALID_STRING = "Phone number invalid"

_error_dict[EMAIL_INVALID_CODE] = EMAIL_INVALID_STRING
_error_dict[PASSWORD_INVALID_CODE] = PASSWORD_INVALID_STRING
_error_dict[NAME_INVALID_CODE] = NAME_INVALID_STRING
_error_dict[PHONE_NUMBER_INVALID_CODE] = PHONE_NUMBER_INVALID_STRING

FAILED_TO_COMMIT_USER_CODE = 201
FAILED_TO_COMMIT_USER_STRING = "Failed to commit user to database"
FAILED_TO_QUERY_FOR_USER_CODE = 202
FAILED_TO_QUERY_FOR_USER_STRING = "Failed to query database for user"

_error_dict[FAILED_TO_COMMIT_USER_CODE] = FAILED_TO_COMMIT_USER_STRING
_error_dict[FAILED_TO_QUERY_FOR_USER_CODE] = FAILED_TO_QUERY_FOR_USER_STRING

USER_WITH_EMAIL_ALREADY_EXISTS_CODE = 301
USER_WITH_EMAIL_ALREADY_EXISTS_STRING = "User with that email already exists"

_error_dict[USER_WITH_EMAIL_ALREADY_EXISTS_CODE] = USER_WITH_EMAIL_ALREADY_EXISTS_STRING

def create_single_error_response(code: int) -> Dict[str, Dict[str, Union[bool, int, str]]]:
    err_object = error_object(code)
    err_list = error_list()
    err_list.add_error(err_object)

    return err_list.to_dict()

def create_multiple_error_response(codes: List[int]) -> Dict[str, Dict[str, Union[bool, int, str]]]:
    err_list = error_list()
    for code in codes:
        err_object = error_object(code)
        err_list.add_error(err_object)
    
    return err_list.to_dict()

def log_error(code: int) -> None:
    if code not in _error_dict:
        logging.error("Called log_error with an invalid error code.")
        raise ValueError("Not a valid code.")

    logging.error(get_error_string(code))


def get_error_string(code: int) -> str:
    if code not in _error_dict:
        logging.error("Called get_error_string with an invalid error code.")
        raise ValueError("Not a valid code.")

    return _error_dict[code]

def log_generic_error(error_string: str, module_name: str=None, function_name: str=None) -> None:
    if function_name is not None and module_name is not None:
        logging.error(module_name + "." + function_name + ": " + error_string)
    elif function_name is not None and module_name is None:
        logging.error(function_name + ": " + error_string)
    else:
        logging.error(error_string)

class error_object:
    def __init__(self, error_code: int) -> None:
        self.error_string = get_error_string(error_code)
        self.error_code = error_code
    
    def to_dict(self) -> Dict[str, Union[bool, int, str]]:
        return vars(self)

class error_list:
    def __init__(self, errors: List[error_object]=None) -> None:
        if errors is None:
            self.errors = []
        else:
            self.errors = errors
    
    def to_dict(self) -> Dict[str, Dict[str, Union[bool, int, str]]]:
        if self.errors is None or len(self.errors) == 0:
            return None
        dic = {}
        dic['errors'] = []
        for error in self.errors:
            dic['errors'].append({'error': error.to_dict()})
        return dic

    def add_error(self, error: error_object) -> None:
        self.errors.append(error)

