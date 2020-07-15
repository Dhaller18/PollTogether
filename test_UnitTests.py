import os
import flask
import unittest
import app as site
from flask import url_for
from app import app


class RoutingTests(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        self.app = app.test_client()

    def tearDown(self):
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

    def tearDown(self):
        pass

    def test_add_answers_NoData(self):
        with app.test_request_context('/question/'):
            mydict = site.add_answers('A')
            expectedDict = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
            self.assertIsNotNone(mydict, "Default dictionary was not created")

    def test_add_answers_NoData_AnswerGiven(self):
        with app.test_request_context('/question/'):
            mydict = site.add_answers('A')
            expectedDict = {'A': 1, 'B': 0, 'C': 0, 'D': 0}
            self.assertEqual(expectedDict, mydict, "Answer not counted")

    # assumes the current question has answer 'A'
    def test_questionPage(self):
        response = self.app.get('/question/', follow_redirects=True)
        ans = {'A': 'A'}
        data = dict(ans=ans)
        self.app.post('/question/', ans=data, follow_redirects=True)

        assert response.request.path == url_for('/question/#')


if __name__ == "__main__":
    unittest.main()
