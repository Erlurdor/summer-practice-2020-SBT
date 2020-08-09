import json
import unittest
from manage import app

unittest.TestLoader.sortTestMethodsUsing = None

class Test(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_0_index(self):
        response = self.app.get('/index', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_1_registration(self):
        info = {'login': 'test@mail.ru', 'password': 'test12345', 'name': 'test'}
        response = self.app.post('/user', data=json.dumps(info), headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 200)

    def test_2_auth_valid_logout(self):
        info = {'login':'test@mail.ru', 'password':'test12345'}

        # Auth test
        response_auth = self.app.post('/auth', data=json.dumps(info), headers={'Content-Type': 'application/json'})
        self.assertEqual(response_auth.status_code, 200)
