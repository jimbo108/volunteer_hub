import unittest
from backend.test.db_interface_test import TestDBInterfaceRegister


def create_suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestDBInterfaceRegister())
    return test_suite

if __name__ == '__main__':
    suite = create_suite()

    runner = unittest.TextTestRunner()
    runner.run(suite)
