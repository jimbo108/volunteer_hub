from unittest.mock import patch
from unittest import TestCase, main
import flask
from app import app
import backend.api.api as api
import backend.api.errors as errors
from backend.data_model.data_model import User


class TestApiRegisterUser(TestCase):

    '''
    mg_[class variable] = mock_global
    gs_[func] = global_setter
    m_[param] = mocked

    '''
    mg__parse_and_validate_login__valid_user = None
    mg__parse_and_validate_login__codes = None

    '''
    You need an app_context even when jsonify is mocked.  
    https://stackoverflow.com/questions/24877025/runtimeerror-working-outside-of-application-context-when-unit-testing-with-py
    '''
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch('flask.jsonify')
    @patch('backend.data_model.db_interface.save_login')
    @patch('backend.api.api._parse_and_validate_login')
    def test__submit_login__req_none__return_code_and_400(self, m_parse_and_validate_login,
                                                          m_save_login, m_jsonify):
        m_parse_and_validate_login.side_effect = self.mock__parse_and_validate_login
        # BOOKMARK: For some reason jsonify is still being called
        m_jsonify.side_effect = self.mock__jsonify

        self.mg__parse_and_validate_login__valid_user = True

        resp, http_code = api.submit_login(None)

        self.assertFalse(self.is_success_response(resp))

        expected_codes = set([errors.REQUEST_INVALID_CODE])
        self.assertTrue(self.contains_only_error_codes(resp, expected_codes))
        self.assertEqual(http_code, 400)

    def is_success_response(self, resp):
        return resp['success'] and 'errors' not in resp

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

    def mock__parse_and_validate_login(self, request):
        if self.mg__parse_and_validate_login__valid_user is None:
            raise ValueError('mg__parse_and_validate_login__valid_user not set explicitly')

        if self.mg__parse_and_validate_login__valid_user:
            user = User(Email='test@test.com', PasswordHash='asdf',
                        FirstName='first', LastName='last',
                        PhoneNumber='111-111-1111')
            return user, None
        else:
            return None, self.mg__parse_and_validate_login__codes

    def mock__jsonify(self, dic):
        return dic

    def gs_set_codes(self, codes):
        self.mg__parse_and_validate_login__codes = codes

if __name__ == '__main__':
    main()