import re
from typing import Tuple, Dict, Any, List, Union
from flask import jsonify
from bcrypt import hashpw
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager
import backend.api.errors as errors
import backend.data_model.db_interface as db_int
import backend.api.secrets as secrets
from backend.data_model.data_model import User, OrganizationRegistrationRequest


'''
===================================================================================
================================LOGIN USER=========================================
===================================================================================
'''

def login_user(request: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    if request is None:
        return _error_response(errors.REQUEST_INVALID_CODE, 400)

    user, error_codes = _parse_and_validate_login(request, False)
    if error_codes is not None:
        return _error_response(error_codes, 400)

    valid_username, error_code = db_int.check_login(user)
    if error_code is not None:
        return _error_response(error_code, 500)

    if not valid_username:
        return _error_response(errors.LOGIN_INVALID_CODE, 422)
    else:
        access_token = create_access_token(identity=user.Email)
        refresh_token = create_refresh_token(identity=user.Email)
        return _success_response(access_token, refresh_token)


'''
===================================================================================
================================REGISTER USER======================================
===================================================================================
'''


def register_user(request: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    error_list = None

    if request is None:
        return _error_response(errors.REQUEST_INVALID_CODE, 400)

    user, error_codes = _parse_and_validate_login(request, True)
    if error_codes is not None:
        return _error_response(error_codes, 400)

    identity_email = user.Email
    error_code = db_int.save_login(user)
    if error_code is not None:
        error_list = errors.create_single_error_response(error_code)

        if error_list.contains_error(errors.USER_WITH_EMAIL_ALREADY_EXISTS_CODE):
            return jsonify(error_list.to_response_dict()), 200

        return jsonify(error_list.to_response_dict()), 500

    access_token = create_access_token(identity=identity_email)
    refresh_token = create_refresh_token(identity=identity_email)
    return _success_response(access_token, refresh_token)


def _create_user(email: str, password: str, last_name: str, phone_number: str, first_name: str = None) -> User:
    hashed_pass = hash_password(password)
    return User(Email=email, PasswordHash=hashed_pass, FirstName=first_name,
                LastName=last_name, PhoneNumber=phone_number)


def _phone_number_regex(phone_number: str) -> bool:
    if re.match(r"\A\d{3}-\d{3}-\d{4}\Z", phone_number):
        return True
    elif re.match(r"\A1\d{3}-\d{3}-\d{4}\Z", phone_number):
        return True
    elif re.match(r"\A\d{10}\Z", phone_number):
        return True
    elif re.match(r"\A1\d{10}\Z", phone_number):
        return True
    return False


def _clean_phone_number(phone_number: str):
    phone_number = phone_number.strip()
    phone_number = phone_number.replace('-', '')

    if len(phone_number) == 10:
        return phone_number
    elif len(phone_number) == 11:
        return phone_number
    else:
        errors.log_generic_error("Phone number with invalid length: " + phone_number,
                                 'backend.api.api', '_clean_phone_number')
        return ""


'''
===================================================================================
==============================ORGANIZATION REQUEST=================================
===================================================================================
'''


def submit_organization_request(request: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    error_list = None

    if request is None:
        return _error_response(errors.REQUEST_INVALID_CODE, 400)

    org_request, error_codes = _parse_and_validate_org_request(request)
    if error_codes is not None:
        return _error_response(error_codes, 400)

    error_code = db_int.save_org_request(org_request)

    if error_code is not None:
        error_list = errors.create_single_error_response(error_code)
        if error_list.contains_error(errors.ORG_OR_ORG_REQUEST_WITH_NAME_ALREADY_EXISTS_CODE):
            return jsonify(error_list.to_response_dict()), 200
        else:
            return jsonify(error_list.to_response_dict()), 500

    return _success_response()


def _parse_and_validate_org_request(request: Dict[str, Any]) -> Tuple[OrganizationRegistrationRequest, List[int]]:
    error_codes = []

    # TODO: Manage User ID with JWT
    org_name = request.get('organization_name')
    message = request.get('message')
    contact_phone_number = request.get('explicit_phone_number')
    contact_email = request.get('email')
    org_url = request.get('organization_url')

    phone_number = _get_phone_number(contact_phone_number)
    email = _get_email(contact_email)

    email_valid = _validate_email(email)
    phone_number_valid = _validate_phone_number(phone_number)
    org_name_valid = _validate_org_name(org_name)
    org_url_valid = _validate_org_url(org_url)

    if not email_valid:
        error_codes.append(errors.EMAIL_INVALID_CODE)

    if not phone_number_valid:
        error_codes.append(errors.PHONE_NUMBER_INVALID_CODE)

    if not org_name_valid:
        error_codes.append(errors.PASSWORD_INVALID_CODE)

    if not org_url_valid:
        error_codes.append(errors.NAME_INVALID_CODE)

    if len(error_codes) > 0:
        return None, error_codes

    org_request = _create_org_request(org_name, message, phone_number,
                                      email, org_url)
    return org_request, None


def _create_org_request(org_name: str, message: str, phone_number: str,
                        email: str, org_url: str):
    # TODO: Add real user ID here
    dummy_user_id = "1"

    return OrganizationRegistrationRequest(SubmittingUserId=dummy_user_id,
                                           OrganizationName=org_name,
                                           Message=message,
                                           ContactPhoneNumber=phone_number,
                                           ContactEmail=email,
                                           OrganizationURL=org_url)


def _validate_password(password: str) -> bool:
    if len(password) < 6:
        return False
    return True


def _validate_name(first_name: str, last_name: str) -> bool:
    return last_name is not None and len(last_name) > 0


def _get_phone_number(phone_number: str) -> str:
    raise NotImplementedError()


def _get_email(email: str) -> str:
    raise NotImplementedError


def _validate_org_name(org_name: str) -> bool:
    return org_name is not None and len(org_name) > 0


def _validate_org_url(org_url: str) -> bool:
    raise NotImplementedError()


'''
===================================================================================
==================================SHARED===========================================
===================================================================================
'''


def _create_success_response(access_token: str = None, refresh_token: str = None) -> Dict[str, Any]:
    return_dict = {'success': True}
    if access_token is not None:
        return_dict['access_token'] = access_token
    if refresh_token is not None:
        return_dict['refresh_token'] = refresh_token
    return return_dict


def _success_response(access_token: str = None, refresh_token: str = None, http_code: int = 200) -> Dict[str, Any]:
    return jsonify(_create_success_response(access_token, refresh_token)), http_code


def _error_response(error_codes: Union[int, List[int]], http_code: int) -> Dict[str, Any]:
    if type(error_codes) == list:
        return jsonify(errors.create_multiple_error_response(error_codes).to_response_dict()), http_code
    else:
        return jsonify(errors.create_single_error_response(error_codes).to_response_dict()), http_code


def hash_password(password: str) -> None:
    return hashpw(password.encode(), secrets.SALT)  # TODO: Make sure passwords are non null


def _validate_email(email: str) -> bool:
    if email is None or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False
    return True


def _validate_phone_number(phone_number: str) -> bool:
    if phone_number is None:
        return False
    phone_number = phone_number.strip()
    if _phone_number_regex(phone_number):
        return True
    return False


def _parse_and_validate_login(request: Dict[str, Any], is_register: bool) -> Tuple[User, List[str]]:
    error_codes = []

    email = request.get('email')
    password = request.get('password')

    email_valid = _validate_email(email)
    password_valid = _validate_password(password)

    if not email_valid:
        error_codes.append(errors.EMAIL_INVALID_CODE)

    if not password_valid:
        error_codes.append(errors.PASSWORD_INVALID_CODE)

    if is_register:
        first_name = request.get('first_name')
        last_name = request.get('last_name')
        phone_number = request.get('phone_number')

        name_valid = _validate_name(first_name, last_name)
        phone_number_valid = _validate_phone_number(phone_number)

        if not name_valid: 
            error_codes.append(errors.NAME_INVALID_CODE)

        if not phone_number_valid:
            error_codes.append(errors.PHONE_NUMBER_INVALID_CODE)

    if len(error_codes) > 0:
        return None, error_codes 

    user = _create_user(email, password, last_name, phone_number, first_name)
    return user, None