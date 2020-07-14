import os
import unittest
from app import app


class RoutingTests(unittest.TestCase):
    # function to set up testing connection
    def setUp(self):
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        self.app = app.test_client()

    # function to teardown connection after testing
    def tear_down(self):
        pass

    def test_homepage(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_aboutpage(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()