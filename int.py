import unittest
from main import app, user_data_storage  # Import user_data_storage from main.py

class AppIntegrationTest(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()




    def test_get_user_intervals_endpoint(self):
        response = self.app.get('/user_intervals')
        self.assertEqual(response.status_code, 200)  #

    def test_get_user_list_endpoint(self):
        response = self.app.get('/api/users/list')
        self.assertEqual(response.status_code, 200)
    def test_get_user_intervals_endpoint_empty(self):

        user_data_storage.clear()
        response = self.app.get('/user_intervals')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {})







