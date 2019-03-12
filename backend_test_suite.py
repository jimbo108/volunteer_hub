import unittest
from backend.test.api_test import TestSubmitLogin


def create_suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestSubmitLogin())
    return test_suite

if __name__ == '__main__':
    suite = create_suite()

    runner = unittest.TextTestRunner()
    runner.run(suite)
