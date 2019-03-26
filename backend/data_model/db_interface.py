from typing import Tuple, Any
import logging
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
import backend.api.errors as errors
from backend.data_model.data_model import (User, Database, OrganizationRegistrationRequest,
                                           Organization)

Session = sessionmaker(bind=Database.Engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

'''
===================================================================================
================================REGISTER===========================================
===================================================================================
'''


def save_login(user: User) -> int:
    """Save a new User to the database."""
    with session_scope() as session:
        return _save_login_internal(user, session)


def _save_login_internal(user: User, session: Session) -> int:
    user_exists = _user_already_exists(user.Email, session)
    error_codes = []

    if user_exists is None:
        errors.log_error(errors.FAILED_TO_QUERY_FOR_USER_CODE) 
        return errors.FAILED_TO_QUERY_FOR_USER_CODE
    elif user_exists:
        errors.log_error(errors.USER_WITH_EMAIL_ALREADY_EXISTS_CODE)
        return errors.USER_WITH_EMAIL_ALREADY_EXISTS_CODE

    try:
        session.add(user)
    except BaseException as e:
        errors.log_error(errors.FAILED_TO_COMMIT_USER_CODE)
        return errors.FAILED_TO_COMMIT_USER_CODE

    return None


def _user_already_exists(email: str, session: Session) -> bool:
    try:
        query = session.query(User).filter_by(Email=email)
        existing_users = query.all()
    except BaseException as e:
        logging.error(errors.FAILED_TO_QUERY_FOR_USER_STRING + ': ' + str(e))
        return None

    if len(existing_users) > 1:
        logging.warning('Found two users with the same email')
        return True
    elif len(existing_users) == 1:
        return True
    else:
        return False

'''
def _get_user_with_email(email: str) -> User:
    with session_scope as session:
        try:
            query = session.query(User).filter_by(Email=email)
            existing_users = query.all()
'''
'''
===================================================================================
==============================REGISTER ORGANIZATION================================
===================================================================================
'''


def save_org_request(org_request: OrganizationRegistrationRequest) -> int:
    with session_scope() as session:
        return _save_org_request_internal(org_request, session)


def _save_org_request_internal(org_request: OrganizationRegistrationRequest, session: Session) -> int:
    org_req_or_org_exists = _org_req_or_org_exists(org_request.OrganizationName)
    error_codes = []

    if org_req_or_org_exists is None:
        errors.log_error(errors.FAILED_TO_QUERY_FOR_ORG_CODE)
        return errors.FAILED_TO_QUERY_FOR_ORG_CODE
    elif org_req_or_org_exists:
        errors.log_error(errors.ORG_OR_ORG_REQUEST_WITH_NAME_ALREADY_EXISTS_CODE)
        return errors.ORG_OR_ORG_REQUEST_WITH_NAME_ALREADY_EXISTS_CODE

    try:
        session.add(org_request)
    except BaseException as e:
        errors.log_error(errors.FAILED_TO_COMMIT_ORG_REQUEST_CODE)
        return errors.FAILED_TO_COMMIT_ORG_REQUEST_CODE

    return None


def _org_req_or_org_exists(organization_name: str, session: Session) -> bool:
    org_req_exists = _org_req_exists(organization_name, session)
    org_exists = _org_exists(organization_name, session)
    return org_exists or org_req_exists


def _org_req_exists(organization_name: str, session: Session) -> bool:
    try:
        query = session.query(OrganizationRegistrationRequest).filter_by(OrganizationName=organization_name)
        existing_org_requests = query.all()
    except:
        errors.log_error(errors.FAILED_TO_QUERY_FOR_ORG_CODE)
        return None

    if len(existing_org_requests) > 0:
        return True

    return False


def _org_exists(organization_name: str, session: Session) -> bool:
    try:
        query = session.query(Organization).filter_by(OrganizationName=organization_name)
        existing_orgs = query.all()
    except:
        errors.log_error(errors.FAILED_TO_QUERY_FOR_ORG_CODE)
        return None

    if len(existing_orgs) > 0:
        return True

    return False

'''
===================================================================================
====================================SHARED=========================================
===================================================================================
'''


def set_database(engine: Any) -> None:
    Session = sessionmaker(bind=engine)
