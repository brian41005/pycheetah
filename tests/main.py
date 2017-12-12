import unittest

if __name__ == '__main__':
    testsuite = unittest.TestLoader().discover('each_test',  pattern="test*.py")
    unittest.TextTestRunner(verbosity=3).run(testsuite)
