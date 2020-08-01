import uuid

from flask import Flask, redirect, url_for, render_template, request, session
from flask_socketio import SocketIO, emit, join_room
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "aklsdfjlksdahfkVdHDKHlkdsjfSDkfj323KDSFhk"
socketio = SocketIO(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pollTogether3.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    owner = db.Column(db.String(50), nullable=False)


class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room = db.Column(db.String(10), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    poll_type = db.Column(db.String(20), default="Pie", nullable=False)
    response_type = db.Column(db.String(20), default="mc", nullable=False)
    show_results = db.Column(db.Boolean, default=True, nullable=False)
    question = db.Column(db.String(100))
    choice1 = db.Column(db.String(100))
    choice2 = db.Column(db.String(100))
    choice3 = db.Column(db.String(100))
    choice4 = db.Column(db.String(100))
    response1 = db.Column(db.Integer, nullable=False)
    response2 = db.Column(db.Integer, nullable=False)
    response3 = db.Column(db.Integer, nullable=False)
    response4 = db.Column(db.Integer, nullable=False)

    def serialize(self):
        return {
            'id' : self.id,
            'room' : self.room,
            'active' : self.active,
            'poll_type' : self.poll_type,
            'response_type' : self.response_type,
            'show_results' : self.show_results,
            'question' : self.question,
            'choice1' : self.choice1,
            'choice2' : self.choice2,
            'choice3' : self.choice3,
            'choice4' : self.choice4,
            'response1' : self.response1,
            'response2' : self.response2,
            'response3' : self.response3,
            'response4' : self.response4
        }

class Participated(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, nullable=False)
    uid = db.Column(db.String(50), nullable=False)


@app.route('/', methods=["POST", "GET"])
def home():
    session.permanent = True
    if 'uid' not in session:
        session['uid'] = str(uuid.uuid1())
    session["user"] = "User001"
    poll_user = session["user"]
    return render_template("home.html", user=poll_user,
                           openRooms=Room.query.all())


@app.route('/joinRoom/', methods=["POST", "GET"])
def join_existing():
    if 'uid' not in session:
        session['uid'] = str(uuid.uuid1())
    if request.method == "POST":
        room = request.form.get('roomName')
        if db.session.query(db.exists().where(Room.name == room)).scalar():
            return redirect(url_for("poll_room", room_id=room))

    return render_template("joinRoom.html")


@app.route("/room/<room_id>/results/<poll_id>")
def results(room_id, poll_id):
    poll = Poll.query.filter_by(id=poll_id).first()
    if poll.room == room_id:
        data = formatPoll(poll)
        return render_template("resultsPage.html", data=data, poll_q=poll.question)
    else:
        redirect(url_for("poll_room", room_id=room_id))


def formatPoll(poll):
    data = {'A': poll.response1,
            'B': poll.response2,
            'C': poll.response3,
            'D': poll.response4}
    return data


@app.route("/room/<room_id>", methods=["POST", "GET"])
def poll_room(room_id):
    if 'uid' not in session:
        session['uid'] = str(uuid.uuid1())
    participated = []
    for entry in Participated.query.filter_by(uid=session['uid']).all():
        participated.append(entry.poll_id)

    room_polls = Poll.query.filter_by(room=room_id).all()
    all_polls = []
    for poll in room_polls:
        all_polls.append(poll.serialize())
    return render_template("pollRoom.html", user=session['uid'],
                           room=Room.query.filter_by(name=room_id).first(),
                           polls=all_polls,
                           answered_polls=participated)


@socketio.on('makepoll')
def on_new_poll(data):
    showResults = False
    if data['show_results'] == "true":
        showResults = True
    new_poll = Poll(room=data['r_id'], question=data['Q'],
                    poll_type=data['poll_type'],
                    response_type=data['response_type'],
                    show_results=showResults,
                    choice1=data['A'], choice2=data['B'],
                    choice3=data['C'], choice4=data['D'],
                    response1=0, response2=0, response3=0,
                    response4=0)
    db.session.add(new_poll)
    db.session.commit()
    add_participated(new_poll.id)
    poll_data = new_poll.serialize()
    #emit('redirect', {'url': url_for("results", room_id=new_poll.room,
                                     #poll_id=new_poll.id)})
    emit('newPoll', poll_data, room=new_poll.room)


@socketio.on('create')
def on_create(data):
    if 'uid' not in session:
        session['uid'] = str(uuid.uuid1())
    rm_id = data['room_id']
    new_room = Room(name=rm_id, owner=session['uid'])
    db.session.add(new_room)
    db.session.commit()
    emit('redirect', {'url': url_for("poll_room", room_id=rm_id)})


@socketio.on('join')
def on_join(data):
    join_room(data['id'])


@socketio.on('pollResponse')
def on_response(data):
    add_participated(data['poll_id'])
    poll = Poll.query.filter_by(id=data['poll_id']).first()
    choice = data['response']
    if isinstance(choice, str):
        add_single_response(poll, choice)
    elif isinstance(choice, list):
        add_multi_response(poll, choice)
    new_data = Poll.query.filter_by(id=data['poll_id']).first()
    emit('responseMade', new_data.serialize(), room=new_data.room)


def add_single_response(poll, choice):
    if choice == 'A':
        poll.response1 = Poll.response1 + 1
    elif choice == 'B':
        poll.response2 = Poll.response2 + 1
    elif choice == 'C':
        poll.response3 = Poll.response3 + 1
    elif choice == 'D':
        poll.response4 = Poll.response4 + 1
    db.session.commit()


def add_multi_response(poll, choices):
    for choice in choices:
        add_single_response(poll, choice)


def add_participated(poll_id):
    if 'uid' not in session:
        session['uid'] = str(uuid.uuid1())
    participated_poll = Participated(poll_id=poll_id, uid=session['uid'])
    db.session.add(participated_poll)
    db.session.commit


if __name__ == '__main__':
    socketio.run(app, debug=True)
