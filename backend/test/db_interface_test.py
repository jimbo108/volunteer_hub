import unittest
import backend.data_model.db_interface as db_interface
from backend.data_model.data_model import Database, User
from sqlalchemy.orm import sessionmaker


class TestDBInterface(unittest.TestCase):

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
        hashed_pass = 'hash'
        db_interface.save_login(email, hashed_pass)

        users = self._get_users_with_email(email)
        self.assertEqual(len(users), 1)

    def test___user_already_exists__no_user__return_false(self):
        email = "testemail@email.com"
        hashed_pass = 'hash'
        exists = None

        with db_interface.session_scope() as session:
            exists = db_interface._user_already_exists(email, session)
        
        self.assertEqual(exists, False)
    
    #def test___user
