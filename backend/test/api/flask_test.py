# From flask.pocoo.org/docs/1.0/testing/

import os
from app import app
import unittest
from backend.data_model.data_model import Database
from backend.data_model.db_interface import set_database, session_scope, _user_already_exists
import backend.api.errors as errors
from backend.test.test_helper import get_valid_register_user_dict


class FlaskTestCase(unittest.TestCase):

    TEST_DB = 'test'

    def setUp(self):
        Database.create_database(self.TEST_DB)
        set_database(Database.Engine)
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        Database.drop_all_test_database(self.TEST_DB)

    def test_one(self):
        ret = self.app.get('/random')
        self.assertTrue(type(ret.json["randomNumber"]) == int)

    def test__register_user__valid_input__user_created(self):
        test_dict = get_valid_register_user_dict()

        ret = self.post_with_user_dict(test_dict)
        self.assertTrue(ret.json.get('success'))
        self.assertIsNone(ret.json.get('errors'))

        with session_scope() as session:
            self.assertTrue(_user_already_exists(test_dict['email'], session))

    def test__register_user__invalid_email_and_phone_number__return_codes_no_user_created(self):
        valid_dict = get_valid_register_user_dict()
        invalid_phone_and_email_dict = {
            'email': 'test_test.com',
            'phone_number': '555-555-555'
            }
        test_dict = self.merge_dicts(valid_dict, invalid_phone_and_email_dict)
        ret = self.post_with_user_dict(test_dict)

        self.assertFalse(ret.json.get('success'))

        expected_error_codes = set([errors.EMAIL_INVALID_CODE, errors.PHONE_NUMBER_INVALID_CODE])
        self.assertTrue(self.contains_only_error_codes(ret.json, expected_error_codes))
        with session_scope() as session:
            self.assertFalse(_user_already_exists(test_dict['email'], session))

    def test__register_user__invalid_password_and_last_name__return_codes_no_user_created(self):
        valid_dict = get_valid_register_user_dict()
        invalid_password_and_last_name_dict = {
            'password': 'fivec',
            'last_name': ''
        }
        test_dict = self.merge_dicts(valid_dict, invalid_password_and_last_name_dict)
        ret = self.post_with_user_dict(test_dict)

        self.assertFalse(ret.json.get('success'))

        expected_error_codes = set([errors.NAME_INVALID_CODE, errors.PASSWORD_INVALID_CODE])
        self.assertTrue(self.contains_only_error_codes(expected_error_codes))

        with session_scope() as session:
            self.assertFalse(_user_already_exists(test_dict['email'], session))

    def test__register_user__no_first_name__user_created(self):
        valid_dict = get_valid_register_user_dict()
        no_first_name_dict = {
            'first_name': ''
        }
        test_dict = self.merge_dicts(valid_dict, no_first_name_dict)
        ret = self.post_with_user_dict(test_dict)

        self.assertTrue(ret.json.get('success'))
        self.assertIsNone(ret.json.get('errors'))

        with session_scope() as session:
            self.assertAlmostEqualstTrue(_user_already_exists(test_dict['email']))

    def post_with_user_dict(self, user_dict):
        return self.app.post('/register-user', json=user_dict, follow_redirects=True)

    def merge_dicts(self, source, target):
        dic = source.copy()
        dic.update(target)
        return dic

    def contains_only_error_codes(self, json, expected_codes_set):
        errors = json.get('errors')
        if errors is None:
            return False

        found_codes_set = set()
        for error in errors:
            error = error.get('error')
            if error is None:
                continue
            error_code = error.get('error_code')
            if error_code is None:
                continue
            found_codes_set.add(error_code)

        symmetric_difference = found_codes_set.symmetric_difference(expected_codes_set)
        return len(symmetric_difference) == 0

if __name__ == '__main__':
    unittest.main()


