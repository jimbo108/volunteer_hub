from unittest.mock import patch
from unittest import TestCase, main
import flask
from app import app
import backend.api.api as api
import backend.api.errors as errors
import backend.data_model.db_interface as db_interface
from backend.data_model.data_model import (
        User, OrganizationRegistrationRequest,
        Database)
from sqlalchemy.orm import sessionmaker
from backend.test.api.flask_test import get_valid_register_user_dict


class TestApiRegisterUser(TestCase):

    '''
    mg_[class variable] = mock_global
    gs_[func] = global_setter
    m_[param] = mocked

    '''

    TEST_DB = 'test'

    app_context = None

    mg__parse_and_validate_login__valid_user = None
    mg__parse_and_validate_login__codes = None
    mg__save_login__successful_save = None
    mg__save_login__code = None

    mg__parse_and_validate_organization_request__valid_org = None
    mg__parse_and_validate_organization_request__codes = None
    mg__save_org_request__successful_save = None
    mg__save_org_request__code = None

    '''
    You need an app_context even when jsonify is mocked.  
    https://stackoverflow.com/questions/24877025/runtimeerror-working-outside-of-application-context-when-unit-testing-with-py
    '''
    @classmethod
    def setUpClass(cls):
        TestApiRegisterUser.app_context = app.app_context()
        TestApiRegisterUser.app_context.push()

    @classmethod
    def tearDownClass(cls):
        TestApiRegisterUser.app_context.pop()

    def setUp(self):
        TestApiRegisterUser.mg__parse_and_validate_login__valid_user = None
        TestApiRegisterUser.mg__parse_and_validate_login__codes = None
        TestApiRegisterUser.mg__save_login__successful_save = None
        TestApiRegisterUser.mg__save_login__code = None
        TestApiRegisterUser.mg__parse_and_validate_organization_request__valid_org = None
        TestApiRegisterUser.mg__parse_and_validate_organization_request__codes = None
        TestApiRegisterUser.mg__save_org_request__successful_save = None
        TestApiRegisterUser.mg__save_org_request__code = None

        Database.create_database(self.TEST_DB)
        db_interface.Session = sessionmaker(bind=Database.Engine)

    def tearDown(self):
        Database.drop_all_test_database(self.TEST_DB)

 

    '''
    ===================================================================================
    ================================REGISTER USER======================================
    ===================================================================================
    '''

    @patch('backend.api.api.jsonify')
    @patch('backend.data_model.db_interface.save_login')
    @patch('backend.api.api._parse_and_validate_login')
    def test__submit_login__req_none__return_code_and_400(self, m_parse_and_validate_login,
                                                          m_save_login, m_jsonify):
        m_parse_and_validate_login.side_effect = self.mock__parse_and_validate_login
        m_jsonify.side_effect = self.mock__jsonify

        TestApiRegisterUser.mg__parse_and_validate_login__valid_user = True

        resp, http_code = api.register_user(None)

        self.assertFalse(self.is_success_response(resp))

        expected_codes = set([errors.REQUEST_INVALID_CODE])
        self.assertTrue(self.contains_only_error_codes(resp, expected_codes))
        self.assertEqual(http_code, 400)

    @patch('backend.api.api.jsonify')
    @patch('backend.data_model.db_interface.save_login')
    @patch('backend.api.api._parse_and_validate_login')
    def test__submit_login__parse_returns_errors__return_codes_and_400(self, m_parse_and_validate_login,
                                                                       m_save_login, m_jsonify):
        m_parse_and_validate_login.side_effect = self.mock__parse_and_validate_login
        m_jsonify.side_effect = self.mock__jsonify

        TestApiRegisterUser.mg__parse_and_validate_login__valid_user = False
        TestApiRegisterUser.mg__parse_and_validate_login__codes = [errors.PASSWORD_INVALID_CODE, errors.EMAIL_INVALID_CODE]

        resp, http_code = api.register_user({"not_none": 1})

        self.assertFalse(self.is_success_response(resp))

        expected_codes = set([errors.PASSWORD_INVALID_CODE, errors.EMAIL_INVALID_CODE])
        self.assertTrue(self.contains_only_error_codes(resp, expected_codes))
        self.assertEqual(http_code, 400)

    @patch('backend.api.api.jsonify')
    @patch('backend.data_model.db_interface.save_login')
    @patch('backend.api.api._parse_and_validate_login')
    def test__submit_login__email_already_exists__return_code_and_200(self, m_parse_and_validate_login,
                                                                      m_save_login, m_jsonify):
        m_parse_and_validate_login.side_effect = self.mock__parse_and_validate_login
        m_save_login.side_effect = self.mock__save_login
        m_jsonify.side_effect = self.mock__jsonify

        TestApiRegisterUser.mg__parse_and_validate_login__valid_user = True
        TestApiRegisterUser.mg__save_login__successful_save = False
        TestApiRegisterUser.mg__save_login__code = errors.USER_WITH_EMAIL_ALREADY_EXISTS_CODE

        resp, http_code = api.register_user({"not_none": 1})

        self.assertFalse(self.is_success_response(resp))

        expected_codes = set([errors.USER_WITH_EMAIL_ALREADY_EXISTS_CODE])
        self.assertTrue(self.contains_only_error_codes(resp, expected_codes))
        self.assertEqual(http_code, 200)

    @patch('backend.api.api.jsonify')
    @patch('backend.data_model.db_interface.save_login')
    @patch('backend.api.api._parse_and_validate_login')
    def test__submit_login__failed_to_commit_user__return_code_and_500(self, m_parse_and_validate_login,
                                                                       m_save_login, m_jsonify):
        m_parse_and_validate_login.side_effect = self.mock__parse_and_validate_login
        m_save_login.side_effect = self.mock__save_login
        m_jsonify.side_effect = self.mock__jsonify

        TestApiRegisterUser.mg__parse_and_validate_login__valid_user = True
        TestApiRegisterUser.mg__save_login__successful_save = False
        TestApiRegisterUser.mg__save_login__code = errors.FAILED_TO_COMMIT_USER_CODE

        resp, http_code = api.register_user({"not_none": 1})

        self.assertFalse(self.is_success_response(resp))

        expected_codes = set([errors.FAILED_TO_COMMIT_USER_CODE])
        self.assertTrue(self.contains_only_error_codes(resp, expected_codes))
        self.assertEqual(http_code, 500)

    @patch('backend.api.api.jsonify')
    @patch('backend.data_model.db_interface.save_login')
    @patch('backend.api.api._parse_and_validate_login')
    def test__submit_login__success__return_success_and_200(self, m_parse_and_validate_login,
                                                            m_save_login, m_jsonify):
        m_parse_and_validate_login.side_effect = self.mock__parse_and_validate_login
        m_save_login.side_effect = self.mock__save_login
        m_jsonify.side_effect = self.mock__jsonify

        TestApiRegisterUser.mg__parse_and_validate_login__valid_user = True
        TestApiRegisterUser.mg__save_login__successful_save = True

        resp, http_code = api.register_user({"not_none": 1})

        self.assertTrue(self.is_success_response(resp))

        self.assertEqual(http_code, 200)

    @patch('backend.api.api._validate_phone_number')
    @patch('backend.api.api._validate_name')
    @patch('backend.api.api._validate_password')
    @patch('backend.api.api._validate_email')
    def test___parse_and_validate_login__success__return_user(self, m_validate_email,
                                                              m_validate_password,
                                                              m_validate_name,
                                                              m_validate_phone_number):
        m_validate_email.return_value = True
        m_validate_password.return_value = True
        m_validate_name.return_value = True
        m_validate_phone_number.return_value = True

        user_req = get_valid_register_user_dict()

        user, errors = api._parse_and_validate_login(user_req, True)

        self.assertTrue(type(user) == User)
        self.assertIsNone(errors)

    @patch('backend.api.api._validate_phone_number')
    @patch('backend.api.api._validate_name')
    @patch('backend.api.api._validate_password')
    @patch('backend.api.api._validate_email')
    def test___parse_and_validate_login__all_invalid__return_errors(self, m_validate_email,
                                                                    m_validate_password,
                                                                    m_validate_name,
                                                                    m_validate_phone_number):
        m_validate_email.return_value = False
        m_validate_password.return_value = False
        m_validate_name.return_value = False
        m_validate_phone_number.return_value = False

        user_req = get_valid_register_user_dict()

        user, error_list = api._parse_and_validate_login(user_req, True)

        self.assertIsNone(user)
        expected_codes = set([errors.EMAIL_INVALID_CODE,
                              errors.PASSWORD_INVALID_CODE,
                              errors.NAME_INVALID_CODE,
                              errors.PHONE_NUMBER_INVALID_CODE])

        self.assertTrue(self.error_list_contains_only_error_codes(error_list, expected_codes))

    #  TODO: Test validation functions
    '''
    ===================================================================================
    ==============================ORGANIZATION REQUEST=================================
    ===================================================================================
    '''

    @patch('backend.api.api.jsonify')
    @patch('backend.data_model.db_interface.save_org_request')
    @patch('backend.api.api._parse_and_validate_org_request')
    def test__submit_org_req__req_none__return_code_and_400(self, m_parse_and_validate_org_request,
                                                            m_save_org_request, m_jsonify):
        m_parse_and_validate_org_request.side_effect = self.mock__parse_and_validate_org_request
        m_jsonify.side_effect = self.mock__jsonify

        TestApiRegisterUser.mg__save_org_request__successful_save = True
        TestApiRegisterUser.mg__parse_and_validate_organization_request__valid_org = True

        resp, http_code = api.submit_organization_request(None)

        self.assertFalse(self.is_success_response(resp))

        expected_codes = set([errors.REQUEST_INVALID_CODE])
        self.assertTrue(self.contains_only_error_codes(resp, expected_codes))
        self.assertEqual(http_code, 400)

    @patch('backend.api.api.jsonify')
    @patch('backend.data_model.db_interface.save_org_request')
    @patch('backend.api.api._parse_and_validate_org_request')
    def test__submit_org_req__parse_returns_errors__return_codes_and_400(self, m_parse_and_validate_org_request,
                                                                         m_save_org_request, m_jsonify):
        m_parse_and_validate_org_request.side_effect = self.mock__parse_and_validate_org_request
        m_jsonify.side_effect = self.mock__jsonify

        TestApiRegisterUser.mg__parse_and_validate_organization_request__valid_org = False
        TestApiRegisterUser.mg__parse_and_validate_organization_request__codes = [errors.PHONE_NUMBER_INVALID_CODE,
                                                                   errors.EMAIL_INVALID_CODE]

        resp, http_code = api.submit_organization_request({"not_none": 1})

        self.assertFalse(self.is_success_response(resp))

        expected_codes = set([errors.PHONE_NUMBER_INVALID_CODE, errors.EMAIL_INVALID_CODE])
        self.assertTrue(self.contains_only_error_codes(resp, expected_codes))
        self.assertEqual(http_code, 400)

    @patch('backend.api.api.jsonify')
    @patch('backend.data_model.db_interface.save_org_request')
    @patch('backend.api.api._parse_and_validate_org_request')
    def test__submit_org_req__failed_to_commit_org__return_codes_and_500(self, m_parse_and_validate_org_request,
                                                                         m_save_org_request, m_jsonify):
        m_parse_and_validate_org_request.side_effect = self.mock__parse_and_validate_org_request
        m_jsonify.side_effect = self.mock__jsonify
        m_save_org_request.side_effect = self.mock__save_org_request

        TestApiRegisterUser.mg__parse_and_validate_organization_request__valid_org = True
        TestApiRegisterUser.mg__save_org_request__successful_save = False
        TestApiRegisterUser.mg__save_org_request__code = errors.FAILED_TO_COMMIT_ORG_REQUEST_CODE

        resp, http_code = api.submit_organization_request({"not_none": 1})

        self.assertFalse(self.is_success_response(resp))

        expected_codes = set([errors.FAILED_TO_COMMIT_ORG_REQUEST_CODE])
        self.assertTrue(self.contains_only_error_codes(resp, expected_codes))
        self.assertEqual(http_code, 500)

    @patch('backend.api.api.jsonify')
    @patch('backend.data_model.db_interface.save_org_request')
    @patch('backend.api.api._parse_and_validate_org_request')
    def test__submit_org_req__success__return_success_and_200(self, m_parse_and_validate_org_request,
                                                              m_save_org_request, m_jsonify):
        m_parse_and_validate_org_request.side_effect = self.mock__parse_and_validate_org_request
        m_jsonify.side_effect = self.mock__jsonify
        m_save_org_request.side_effect = self.mock__save_org_request

        TestApiRegisterUser.mg__parse_and_validate_organization_request__valid_org = True
        TestApiRegisterUser.mg__save_org_request__successful_save = True

        resp, http_code = api.submit_organization_request({"not_none": 1})

        self.assertTrue(self.is_success_response(resp))

        self.assertEqual(http_code, 200)

    '''
    @patch('backend.api.api._validate_phone_number')
    @patch('backend.api.api._validate_name')
    @patch('backend.api.api._validate_password')
    @patch('backend.api.api._validate_email')
    def test___parse_and_validate_login__success__return_user(self, m_validate_email,
                                                              m_validate_password,
                                                              m_validate_name,
                                                              m_validate_phone_number):
        m_validate_email.return_value = True
        m_validate_password.return_value = True
        m_validate_name.return_value = True
        m_validate_phone_number.return_value = True

        user_req = get_valid_register_user_dict() 

        user, errors = api._parse_and_validate_login(user_req)

        self.assertTrue(type(user) == User)
        self.assertIsNone(errors)


    @patch('backend.api.api._validate_phone_number')
    @patch('backend.api.api._validate_name')
    @patch('backend.api.api._validate_password')
    @patch('backend.api.api._validate_email')
    def test___parse_and_validate_login__success__return_user(self, m_validate_email,
                                                              m_validate_password,
                                                              m_validate_name,
                                                              m_validate_phone_number):
        m_validate_email.return_value = True
        m_validate_password.return_value = True
        m_validate_name.return_value = True
        m_validate_phone_number.return_value = True

        user_req = get_valid_register_user_dict() 

        user, errors = api._parse_and_validate_login(user_req)

        self.assertTrue(type(user) == User)
        self.assertIsNone(errors)

    @patch('backend.api.api._validate_phone_number')
    @patch('backend.api.api._validate_name')
    @patch('backend.api.api._validate_password')
    @patch('backend.api.api._validate_email')
    def test___parse_and_validate_login__all_invalid__return_errors(self, m_validate_email,
                                                                    m_validate_password,
                                                                    m_validate_name,
                                                                    m_validate_phone_number):
        m_validate_email.return_value = False
        m_validate_password.return_value = False
        m_validate_name.return_value = False
        m_validate_phone_number.return_value = False

        user_req = get_valid_register_user_dict() 

        user, error_list = api._parse_and_validate_login(user_req)

        self.assertIsNone(user)
        expected_codes = set([errors.EMAIL_INVALID_CODE,
                              errors.PASSWORD_INVALID_CODE,
                              errors.NAME_INVALID_CODE,
                              errors.PHONE_NUMBER_INVALID_CODE])

        self.assertTrue(self.error_list_contains_only_error_codes(error_list, expected_codes))

    '''
    # def test__submit_organization_request(self, m_parse_and_validate_org_request):
    #   m_parse_and_validate_org_request.return_value = 

    def is_success_response(self, resp):
        return resp['success'] and 'errors' not in resp

    def error_list_contains_only_error_codes(self, error_list, expected_codes_set):
        found_codes_set = set([error.error_code for error in error_list.errors])
        symmetric_difference = found_codes_set.symmetric_difference(expected_codes_set)
        return len(symmetric_difference) == 0
    
    
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

    def mock__save_login(self, user):
        if TestApiRegisterUser.mg__save_login__successful_save is None:
            raise ValueError('mg__save_login__successful_save not set explicitly')

        if TestApiRegisterUser.mg__save_login__successful_save:
            if TestApiRegisterUser.mg__save_login__code is not None:
                raise ValueError('mg__save_login__code is set while mg__save_login__successful_save is True')
            return None
        else:
            if TestApiRegisterUser.mg__save_login__code is None:
                raise ValueError('mg__save_login__code is not set while mg__save_login__successful_save is False')
            return TestApiRegisterUser.mg__save_login__code

    def mock__save_org_request(self, org_request):
        if TestApiRegisterUser.mg__save_org_request__successful_save is None:
            raise ValueError('mg__save_org_request__successful_save not set explicitly')

        if TestApiRegisterUser.mg__save_org_request__successful_save:
            if TestApiRegisterUser.mg__save_org_request__code is not None:
                raise ValueError('mg__save_org_request__code is set while mg__save_org_request__successful_save is True')
            return None
        else:
            if TestApiRegisterUser.mg__save_org_request__code is None:
                raise ValueError('mg__save_org_request__code is not set while mg__save_org_request__successful_save is False')
            return TestApiRegisterUser.mg__save_org_request__code

    def mock__parse_and_validate_login(self, request, is_register):
        if TestApiRegisterUser.mg__parse_and_validate_login__valid_user is None:
            raise ValueError('mg__parse_and_validate_login__valid_user not set explicitly')

        if TestApiRegisterUser.mg__parse_and_validate_login__valid_user:
            user = User(Email='test@test.com', PasswordHash='asdf',
                        FirstName='first', LastName='last',
                        PhoneNumber='111-111-1111')
            return user, None
        else:
            return None, TestApiRegisterUser.mg__parse_and_validate_login__codes

    def mock__parse_and_validate_org_request(self, request):
        if TestApiRegisterUser.mg__parse_and_validate_organization_request__valid_org is None:
            raise ValueError('mg__parse_and_validate_org_request__valid_org not set explicitly') 

        if TestApiRegisterUser.mg__parse_and_validate_organization_request__valid_org:
            org_request = OrganizationRegistrationRequest(SubmittingUserId=1,
                                                          OrganizationName="Test Org",
                                                          Message="Please",
                                                          ContactPhoneNumber='111-111-1111',
                                                          ContactEmail='test@test.com',
                                                          OrganizationURL='test.com')
            return org_request, None
        else:
            return None, TestApiRegisterUser.mg__parse_and_validate_organization_request__codes

    def mock__jsonify(self, dic):
        return dic

    def raise_error(self):
        raise ValueError("TEST")

    def gs_set_codes(self, codes):
        self.mg__parse_and_validate_login__codes = codes

if __name__ == '__main__':
    main()
