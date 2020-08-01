import unittest
import app as site
from app import app, socketio
from ddt import ddt, data, unpack

pollroom = 'Ymbq'


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
        response = self.app.get('/room/Ymbq', follow_redirects=True)
        self.assertEqual(response.status_code, 200, "questions page could not be loaded")

    def test_questionPageLoaded(self):
        response = self.app.get('/room/Ymbq', content_type='html/text')
        self.assertTrue(b'Welcome to Room: ' in response.data)

    def test_joinRoom(self):
        response = self.app.get('/joinRoom/', content_type='html/text')
        self.assertEqual(response.status_code, 200, "joinRoom page could not be loaded")

    def test_joinRoomLoaded(self):
        response = self.app.get('/joinRoom/', content_type='html/text')
        self.assertTrue(b'Room ID:' in response.data)


@ddt
class TestPoll(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        self.app = app.test_client()
        self.client = socketio.test_client(app, flask_test_client=self.app)

    def tearDown(self):
        pass

    def test_formatPoll(self):
        new_poll = site.Poll(response1=1, response2=2, response3=3, response4=0)
        expected_poll = {'A': 1, 'B': 2, 'C': 3, 'D': 0}
        new_poll = site.format_poll(new_poll)
        self.assertEqual(expected_poll, new_poll, "Poll was not formatted as expected")

    @unpack
    @data({'first': 'mc', 'second': 'Pie', 'third': 'true'},
          {'first': 'ma', 'second': 'bar', 'third': 'false'})
    def test_createQuestion(self, first, second, third):
        with app.test_request_context('/room/Ymbq/'):
            new_poll = {'r_id': 'Ymbq', 'Q': 'Test question', 'A': 'testA', 'B': 'testB', 'C': 'testC',
                        'D': 'testD', 'choice1': 0, 'choice2': 0, 'choice3': 0, 'choice4': 0, 'show_results':
                        third, 'poll_type': second, 'response_type': first}
            response = self.app.get('/room/Ymbq', follow_redirects=True)
            self.client.emit('makepoll', new_poll)
            self.assertTrue(b'Current Polls:' in response.data)

    @unpack
    @data({'response': ['A', 'B', 'C', 'D']},
          {'response': 'A'})
    def test_Response(self, response):
        with app.test_request_context('/room/Ymbq/'):
            new_poll = {'poll_id': 38, 'response': response}
            response = self.app.get('/room/Ymbq', follow_redirects=True)
            self.client.emit('pollResponse', new_poll)

            self.assertTrue(b'Current Polls:' in response.data)

    def test_createNew(self):
        with app.test_request_context('/room/Ymbi/'):
            new_poll = {'room_id': 'Ymbi'}

            response = self.app.get('/room/Ymbi', follow_redirects=True)

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

    # expects there to be a room with the ID Ymbq
    def test_roomJoined(self):
        with app.test_request_context('/joinRoom'):
            response = self.app.post('/joinRoom/', data={'roomName': 'Ymbq'}, follow_redirects=True)
        self.assertTrue(b'Welcome to Room: Ymbq' in response.data)


if __name__ == "__main__":
    unittest.main()
