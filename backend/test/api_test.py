import unittest
import backend.api.api as api

# TODO Finish this class
class TestSubmitLogin(unittest.TestCase):

    SaveUserCalled = False

   # @patch('backend.data_model.db_interface.')
    def test__parse_and_validate_login__valid_input__return_true(self):
        #db_interface_mock.save_login = lambda x,y: self.SaveUserCalled = True
        request = {"email": "jurban34@gmail.com",
                   "password": "bilbo"}
        response, response_code = api._parse_and_validate_login(request)
        self.assertEqual(1,0)
        self.assertEqual(response['success'], True)
    
    def runTest(self):
        pass
