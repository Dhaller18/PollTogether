import os
import flask
import uuid
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
        self.assertEqual(response.status_code, 200, "Homepage could not not be loaded")

    def test_homePageLoaded(self):
        response = self.app.get('/', content_type='html/text')
        self.assertTrue(b'Would you like to:' in response.data)

    def test_questionPage(self):
        response = self.app.get('/question/', follow_redirects=True)
        self.assertEqual(response.status_code, 200, "questions page could not be loaded")

    def test_questionPageLoaded(self):
        response = self.app.get('/question/', content_type='html/text')
        self.assertTrue(b'What option do you think is correct?' in response.data)

    def test_joinRoom(self):
        response = self.app.get('/joinRoom/', content_type='html/text')
        self.assertEqual(response.status_code, 200, "joinRoom page could not be loaded")

    def test_joinRoomLoaded(self):
        response = self.app.get('/joinRoom/', content_type='html/text')
        self.assertTrue(b'Room ID:' in response.data)


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
            self.assertIsNotNone(mydict, "Default dictionary was not created")

    def test_add_answers_NoData_AnswerGiven(self):
        with app.test_request_context('/question/'):
            mydict = site.add_answers('A')
            expectedDict = {'A': 1, 'B': 0, 'C': 0, 'D': 0}
            self.assertEqual(expectedDict, mydict, "Answer not counted")

    # assumes the current question has answer 'A'
    def test_questionPageWithData(self):
        with app.test_request_context('/question/'):
            response = self.app.post(
                '/question/',
                data={'ans': 'A'},
                follow_redirects=True
            )
        self.assertTrue(b'Results to question' in response.data)

    def test_resultsNoData(self):
        response = self.app.get('/results/', follow_redirects=True)
        self.assertTrue(b'What option do you think is correct?' in response.data, "Was not redirected to questions page")



class TestRooms(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    # expects there to be a room with the ID XEOW
    def test_roomJoined(self):
        with app.test_request_context('/joinRoom'):
            response = self.app.post(
                '/joinRoom/',
                data={'roomName': 'XEOW'},
                follow_redirects=True
            )
        self.assertTrue(b'Welcome to Room: XEOW' in response.data)


if __name__ == "__main__":
    unittest.main()
