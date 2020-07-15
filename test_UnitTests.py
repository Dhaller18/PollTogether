import os
import unittest

from flask import url_for

from app import app


class RoutingTests(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        self.app = app.test_client()

    def tear_down(self):
        pass

    def test_homePage(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_questionPage(self):
        response = self.app.get('/question/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


class TestQuestions(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        self.app = app.test_client()

    def tear_down(self):
        pass

    # assumes the current question is
    def test_questionPage(self):
        response = self.app.get('/question/', follow_redirects=True)
        ans = {'A': 'A'}
        data = dict(ans=ans)
        self.app.post('/question/', ans=data, follow_redirects=True)

        assert response.request.path == url_for('/question/#')


if __name__ == "__main__":
    unittest.main()
