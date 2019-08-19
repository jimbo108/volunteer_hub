import unittest
import backend.data_model.db_interface as db_interface
from backend.data_model.data_model import Database, User
from sqlalchemy.orm import sessionmaker
from backend.api.api import _create_user

class TestDBInterfaceRegister(unittest.TestCase):

    TEST_DB = 'test'

    def setUp(self):
        Database.create_database(self.TEST_DB)
        db_interface.Session = sessionmaker(bind=Database.Engine)
        # TODO: Think of a better paradigm for testing

    def tearDown(self):
        Database.drop_all_test_database(self.TEST_DB)

    def _get_users_with_email(self, email):
        with db_interface.session_scope() as session:
            query = session.query(User).filter_by(Email=email)
            users = query.all()
            return users

    def _insert_user_with_email(self, email, hash):
        with db_interface.session_scope() as session:
            user = User(Email=email, PasswordHash=hash)
            session.add(user)

    def test__save_login__insert_user__user_exists(self):
        email = "testemail@email.com"
        password = 'hash'
        last_name = "last"
        first_name = "first"
        phone_number = "6086086008"

        user = _create_user(email, password, last_name, phone_number, first_name)
    
        db_interface.save_login(user)

        users = self._get_users_with_email(email)
        self.assertEqual(len(users), 1)

    def test__user_already_exists__no_user__return_false(self):
        email = "testemail@email.com"
        exists = None

        with db_interface.session_scope() as session:
            exists = db_interface._user_already_exists(email, session)
        
        self.assertEqual(exists, False)
    
    def test__user_already_exists__multiple_users__return_true(self):
        email = "testemail@email.com"
        password = 'hash'
        last_name = "last"
        first_name = "first"
        phone_number = "6086086008"

        user = _create_user(email, password, last_name, phone_number, first_name)
        db_interface.save_login(user)

        user = _create_user(email, password, last_name, phone_number, first_name) 
        db_interface.save_login(user)

        with db_interface.session_scope() as session:
            exists = db_interface._user_already_exists(email, session)

        self.assertEqual(exists, True)
    
if __name__ == '__main__':
    unittest.main()