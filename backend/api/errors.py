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
REQUEST_INVALID_CODE = 105
REQUEST_INVALID_STRING = "Request was invalid"

_error_dict[EMAIL_INVALID_CODE] = EMAIL_INVALID_STRING
_error_dict[PASSWORD_INVALID_CODE] = PASSWORD_INVALID_STRING
_error_dict[NAME_INVALID_CODE] = NAME_INVALID_STRING
_error_dict[PHONE_NUMBER_INVALID_CODE] = PHONE_NUMBER_INVALID_STRING
_error_dict[REQUEST_INVALID_CODE] = REQUEST_INVALID_STRING

FAILED_TO_COMMIT_USER_CODE = 201
FAILED_TO_COMMIT_USER_STRING = "Failed to commit user to database"
FAILED_TO_QUERY_FOR_USER_CODE = 202
FAILED_TO_QUERY_FOR_USER_STRING = "Failed to query database for user"
FAILED_TO_COMMIT_ORG_REQUEST_CODE = 203
FAILED_TO_COMMIT_ORG_REQUEST_STRING = "Failed to commit organization request to database"
FAILED_TO_QUERY_FOR_ORG_CODE = 204
FAILED_TO_QUERY_FOR_ORG_STRING = "Failed to query database for organization or organization request"

_error_dict[FAILED_TO_COMMIT_USER_CODE] = FAILED_TO_COMMIT_USER_STRING
_error_dict[FAILED_TO_QUERY_FOR_USER_CODE] = FAILED_TO_QUERY_FOR_USER_STRING
_error_dict[FAILED_TO_QUERY_FOR_ORG_CODE] = FAILED_TO_QUERY_FOR_ORG_STRING
_error_dict[FAILED_TO_COMMIT_ORG_REQUEST_CODE] = FAILED_TO_COMMIT_ORG_REQUEST_STRING

USER_WITH_EMAIL_ALREADY_EXISTS_CODE = 301
USER_WITH_EMAIL_ALREADY_EXISTS_STRING = "User with that email already exists"
ORG_OR_ORG_REQUEST_WITH_NAME_ALREADY_EXISTS_CODE = 302
ORG_OR_ORG_REQUEST_WITH_NAME_ALREADY_EXISTS_STRING = "Organization with that name already exists or is being requested."

_error_dict[USER_WITH_EMAIL_ALREADY_EXISTS_CODE] = USER_WITH_EMAIL_ALREADY_EXISTS_STRING
_error_dict[ORG_OR_ORG_REQUEST_WITH_NAME_ALREADY_EXISTS_CODE] = ORG_OR_ORG_REQUEST_WITH_NAME_ALREADY_EXISTS_STRING


def create_single_error_response(code: int) -> Dict[str, Dict[str, Union[bool, int, str]]]:
    err_object = ErrorObject(code)
    err_list = ErrorList()
    err_list.add_error(err_object)

    return err_list


def create_multiple_error_response(codes: List[int]) -> Dict[str, Dict[str, Union[bool, int, str]]]:
    err_list = ErrorList()
    for code in codes:
        err_object = ErrorObject(code)
        err_list.add_error(err_object)

    return err_list


# Format:
#      [CODE] : [MODULE_NAME] : [FUNCTION_NAME] : [ERROR_STRING OR OVERRIDE]
def log_error(code: int=None, error_string_override: str=None, module_name: str=None,
              function_name: str=None) -> None:
    if code is not None and code not in _error_dict:
        logging.error("Called log_error with an invalid error code.")
        raise ValueError("Not a valid code.")

    err_parts = []
    err_string = None

    if code is not None:
        err_parts.append(code)
    if module_name is not None:
        err_parts.append(module_name)
    if function_name is not None:
        err_parts.append(function_name)

    if error_string_override is not None:
        err_string = error_string_override
    elif code is not None:
        err_string = get_error_string(code)
    else:
        raise ValueError("log_error called with no code or error_string_override")

    err_parts.append(err_string)

    full_error_string = ""
    for i, part in enumerate(err_parts):
        if i != 0:
            full_error_string += ":"
        full_error_string += str(part)

    logging.error(full_error_string)


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


class ErrorObject:
    def __init__(self, error_code: int) -> None:
        self.error_string = get_error_string(error_code)
        self.error_code = error_code

    def to_dict(self) -> Dict[str, Union[bool, int, str]]:
        return vars(self)


class ErrorList:
    def __init__(self, errors: List[ErrorObject]=None) -> None:
        if errors is None:
            self.errors = []
            self._error_set = set()
        else:
            self.errors = errors
            self._error_set = set([err.error_code for err in self.errors])

    def to_response_dict(self) -> Dict[str, Dict[str, Union[bool, int, str]]]:
        if self.errors is None or len(self.errors) == 0:
            return None
        dic = {}
        dic['errors'] = []
        for error in self.errors:
            dic['errors'].append({'error': error.to_dict()})
        dic['success'] = False
        return dic

    def add_error(self, error: ErrorObject) -> None:
        self.errors.append(error)
        self._error_set.add(error.error_code)

    def contains_error(self, error_code: int) -> bool:
        return (error_code in self._error_set)
