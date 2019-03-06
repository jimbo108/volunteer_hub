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
        self.hashed_password = hashpw(password.encode(), secrets.SALT)


def submit_login(request: Dict[str, Any]) -> Tuple[Dict[str, object], int]:
    user, err_response = _parse_and_validate_login(request)
    if err_response is not None:
        return jsonify(err_response), 400

    err_response = db_int.save_login(user.email, user.hashed_password)
    if err_response is not None:
        return jsonify(err_response), 500

    success_response = _create_success_response()
    return jsonify(success_response), 200


def _parse_and_validate_login(request: Dict[str, object]) -> Tuple[User, Dict[str, object]]:
    email = request.get('email')
    password = request.get('password')

    email_valid = _validate_email(email)
    password_valid = _validate_password(password)

    if not email_valid:
        error_response = {'success': False,
                          'error_code': errors.EMAIL_INVALID_CODE,
                          'error_string': errors.EMAIL_INVALID_STRING}
        return None, error_response

    if not password_valid:
        error_response = {'success': False,
                          'error_code': errors.PASSWORD_INVALID_CODE,
                          'error_string': errors.PASSWORD_INVALID_STRING}
        return None, error_response

    user = User(email, password)
    return user, None


def _validate_email(email: str) -> bool:
    if email is None or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False
    return True


def _validate_password(password: str) -> bool:
    if len(password) < 6:
        return False
    return True


def _create_success_response():
    return {'success': True}
