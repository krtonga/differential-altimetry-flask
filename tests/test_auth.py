import unittest, json, sys
from app.models import User

class UserModelCase(unittest.TestCase):
    def test_password_hashing(self):
        u = User(username='admin')
        u.set_password('dog')
        self.assertFalse(u.check_password('god'))
        self.assertTrue(u.check_password('dog'))

if __name__ == '__main__':
    unittest.main(verbosity=2)