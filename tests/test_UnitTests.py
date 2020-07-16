import unittest
import app as site
from app import app, socketio

pollroom = 'kdrl'


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
        response = self.app.get('/room/kdrl', follow_redirects=True)
        self.assertEqual(response.status_code, 200, "questions page could not be loaded")

    def test_questionPageLoaded(self):
        response = self.app.get('/room/kdrl', content_type='html/text')
        self.assertTrue(b'Welcome to Room: ' in response.data)

    def test_joinRoom(self):
        response = self.app.get('/joinRoom/', content_type='html/text')
        self.assertEqual(response.status_code, 200, "joinRoom page could not be loaded")

    def test_joinRoomLoaded(self):
        response = self.app.get('/joinRoom/', content_type='html/text')
        self.assertTrue(b'Room ID:' in response.data)

    def test_results(self):
        response = self.app.get('/room/kdrl/results/9', content_type='html/text')
        self.assertEqual(response.status_code, 200, "joinRoom page could not be loaded")

    def test_resultsLoaded(self):
        response = self.app.get('/room/kdrl/results/9', content_type='html/text')
        self.assertTrue(b'Results to question' in response.data)

    def test_resultsWrongPollID(self):
        response = self.app.get('/room/kdrl/results/1', content_type='html/text', follow_redirects=True)
        self.assertTrue(b'No polls yet...' in response.data)


class TestCreatePoll(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        self.app = app.test_client()
        self.client = socketio.test_client(app, flask_test_client=self.app)

    def tearDown(self):
        self.client = socketio.test_client(app, flask_test_client=self.app)
        pass

    def test_formatPoll(self):
        expected_poll = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        new_poll = site.Poll(room='kdrl', question='Test question',
                             choice1='testA', choice2='testB',
                             choice3='testC', choice4='testD',
                             response1=0, response2=0, response3=0,
                             response4=0)
        new_poll = site.format_poll(new_poll)
        self.assertEqual(expected_poll, new_poll, "Poll was not formatted as expected")

    def test_createQuestion(self):
        with app.test_request_context('/room/kdrl/'):
            new_poll = {'r_id': 'kdrl', 'Q': 'Test question', 'A': 'testA', 'B': 'testB', 'C': 'testC',
                        'D': 'testD', 'choice1': 0, 'choice2': 0, 'choice3': 0, 'choice4': 0}
            response = self.app.get('/room/kdrl', follow_redirects=True)
            self.client.emit('makepoll', new_poll)
            self.assertTrue(b'Current Polls:' in response.data)

# Due to the lack of a drop function, this method requires the room to be made new before running the test. Uncomment
# test before running the final test.
    def test_createNewPoll(self):
        with app.test_request_context('/room/kdro/'):
            new_poll = {'room_id': 'kdro'}

            response = self.app.get('/room/kdro', follow_redirects=True)

            self.client.emit('create', new_poll)
            self.assertTrue(b'Current Polls:' in response.data)


class TestRooms(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        self.app = app.test_client()
        self.client = socketio.test_client(app, flask_test_client=self.app)

    def tearDown(self):
        self.client = socketio.test_client(app, flask_test_client=self.app)
        pass

    # expects there to be a room with the ID kdrl
    def test_roomJoined(self):
        with app.test_request_context('/joinRoom'):
            response = self.app.post(
                '/joinRoom/',
                data={'roomName': 'kdrl'},
                follow_redirects=True
            )
        self.assertTrue(b'Welcome to Room: kdrl' in response.data)


if __name__ == "__main__":
    unittest.main()
