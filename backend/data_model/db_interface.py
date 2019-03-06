from typing import Tuple
import logging
from contextlib import contextmanager
from backend.data_model.data_model import User, Database
from sqlalchemy.orm import sessionmaker
import backend.api.errors as errors

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


def save_login(email: str, hashed_password: str) -> Tuple[int, str]:
    """Save a new User to the database."""
    with session_scope() as session:
        return _save_login_internal(email, hashed_password, session)


def _save_login_internal(email: str, hashed_password: str, session: Session) -> Tuple[int, str]:
    user_exists = _user_already_exists(email, session)
    if user_exists is None:
        return (errors.FAILED_TO_QUERY_FOR_USER_CODE,
                errors.FAILED_TO_QUERY_FOR_USER_STRING)
    elif user_exists:
        return(errors.USER_WITH_EMAIL_ALREADY_EXISTS_CODE,
               errors.USER_WITH_EMAIL_ALREADY_EXISTS_STRING)

    user = User(Email=email, PasswordHash=hashed_password)
    try:
        session.add(user)
    except BaseException as e:
        logging.error(errors.FAILED_TO_COMMIT_USER_STRING + ': ' + str(e))
        return (errors.FAILED_TO_COMMIT_USER_CODE,
                errors.FAILED_TO_COMMIT_USER_STRING)

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
