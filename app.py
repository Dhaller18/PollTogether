import uuid

from flask import Flask, redirect, url_for, render_template, request, session
from flask_socketio import SocketIO, emit, join_room
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "aklsdfjlksdahfkVdHDKHlkdsjfSDkfj323KDSFhk"
socketio = SocketIO(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pollTogether.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    owner = db.Column(db.String(50), nullable=False)


class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room = db.Column(db.String(10), nullable=False)
    question = db.Column(db.String(100))
    choice1 = db.Column(db.String(100))
    choice2 = db.Column(db.String(100))
    choice3 = db.Column(db.String(100))
    choice4 = db.Column(db.String(100))
    response1 = db.Column(db.Integer, nullable=False)
    response2 = db.Column(db.Integer, nullable=False)
    response3 = db.Column(db.Integer, nullable=False)
    response4 = db.Column(db.Integer, nullable=False)


@app.route('/', methods=["POST", "GET"])
def home():
    session["user"] = "I am a user"
    poll_user = session["user"]
    # session["data"] = {'A': 1, 'B': 1, 'C': 1, 'D': 1}
    return render_template("home.html", user=poll_user,
                           openRooms=Room.query.all())


@app.route('/joinRoom/', methods=["POST", "GET"])
def join_existing():
    if request.method == "POST":
        room = request.form.get('roomName')
        if db.session.query(db.exists().where(Room.name == room)).scalar():
            return redirect(url_for("poll_room", room_id=room))

    return render_template("joinRoom.html")


@app.route("/question/", methods=["POST", "GET"])
def question():
    if request.method == "POST":
        session['recentAns'] = request.form['ans']
        add_answers(request.form['ans'])
        return redirect(url_for("results"))

    else:
        return render_template("submitAnswers.html")




# Creates a dictionary, data, in session if it does not already exist.
# Checks for the key in the dictionary that matches the param ans and increments its value.
def add_answers(ans):
    if "data" not in session:
        session["data"] = {'A': 0, 'B': 0, 'C': 0, 'D': 0}

    mydict = session["data"]

    for entry in mydict:
        if ans == entry:
            mydict[entry] += 1
    return mydict


@app.route("/room/<room_id>/results/<poll_id>")
def results(room_id, poll_id):
    poll = Poll.query.filter_by(id=poll_id).first()
    if poll.room == room_id:
        data = formatPoll(poll)
        return render_template("resultsPage.html", data=data,
                               poll_q=poll.question)
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
    return render_template("pollRoom.html", user=session['uid'],
                           room=Room.query.filter_by(name=room_id).first())


@socketio.on('makepoll')
def on_new_poll(data):
    new_poll = Poll(room=data['r_id'], question=data['Q'],
                    choice1=data['A'], choice2=data['B'],
                    choice3=data['C'], choice4=data['D'],
                    response1=0, response2=0, response3=0,
                    response4=0)
    db.session.add(new_poll)
    db.session.commit()
    poll_data = {'id': new_poll.id,
                 'room': new_poll.room,
                 'question': new_poll.question,
                 'choice1': new_poll.choice1,
                 'choice2': new_poll.choice2,
                 'choice3': new_poll.choice3,
                 'choice4': new_poll.choice4}
    emit('redirect', {'url': url_for("results", room_id=new_poll.room,
                                     poll_id=new_poll.id)})
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
    poll = Poll.query.filter_by(id=data['poll_id']).first()
    choice = data['response']
    if choice == 'A':
        poll.response1 = Poll.response1 + 1
    elif choice == 'B':
        poll.response2 = Poll.response2 + 1
    elif choice == 'C':
        poll.response3 = Poll.response3 + 1
    elif choice == 'D':
        poll.response4 = Poll.response4 + 1
    db.session.commit()


if __name__ == '__main__':
    socketio.run(app, debug=True)
