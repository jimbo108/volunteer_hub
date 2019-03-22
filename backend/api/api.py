import re
from typing import Tuple, Dict, Any
from flask import jsonify
from bcrypt import hashpw
import backend.api.errors as errors
import backend.data_model.db_interface as db_int
import backend.api.secrets as secrets

class User:
    def __init__(self, email: str, password: str) -> None:
        self.email = email
        self.hashed_password = self._hash_password(password)

    def _hash_password(self, password: str) -> None:
        return hashpw(password.encode(), secrets.SALT) # TODO: Make sure passwords are non null
        

def submit_login(request: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    user, err_response = _parse_and_validate_login(request)
    if err_response is not None:
        return jsonify(err_response), 400

    err_response = db_int.save_login(user.email, user.hashed_password)

    if err_response['error_code'] == errors.USER_WITH_EMAIL_ALREADY_EXISTS_CODE:
        return jsonify(err_response), 200
    elif err_response is not None:
        return jsonify(err_response), 500

    success_response = _create_success_response()
    return jsonify(success_response), 200


def _parse_and_validate_login(request: Dict[str, Any]) -> Tuple[User, Dict[str, object]]:
    error_codes = []

    email = request.get('email')
    password = request.get('password')
    first_name = request.get('first_name')
    last_name = request.get('last_name')
    phone_number = request.get('phone_number')

    email_valid = _validate_email(email)
    password_valid = _validate_password(password)
    name_valid = _validate_name(first_name, last_name)
    phone_number_valid = _validate_phone_number(phone_number)

    if not email_valid:
        error_codes.append(errors.EMAIL_INVALID_CODE)

    if not password_valid:
        error_codes.append(errors.PASSWORD_INVALID_CODE)

    if not name_valid:
        error_codes.append(errors.NAME_INVALID_CODE)
   
    if not phone_number_valid:
        error_codes.append(errors.PHONE_NUMBER_INVALID_CODE)

    user = User(email, password)
    return user, errors.create_multiple_error_response(error_codes)


def _validate_email(email: str) -> bool:
    if email is None or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False
    return True


def _validate_password(password: str) -> bool:
    if len(password) < 6:
        return False
    return True

def _validate_name(first_name: str, last_name: str) -> bool:
    return last_name is not None and len(last_name) > 0

def _validate_phone_number(phone_number: str) -> bool:
    if phone_number is None:
        return False
    phone_number = phone_number.strip()
    if _phone_number_regex(phone_number):
        return True
    return False

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
        errors.log_generic_error("Phone number with invalid length: " + phone_number, 'backend.api.api', '_clean_phone_number')
        return ""

def _create_success_response():
    return {'success': True}
