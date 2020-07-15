from flask import Flask, redirect, url_for, render_template, request, session
from flask_socketio import SocketIO, disconnect, emit, join_room
from poll import PollRoom, Poll
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "hello"
socketio = SocketIO(app)
ROOMS = {}


@app.route('/', methods=["POST", "GET"])
def home():
    session["user"] = "I am a user"
    poll_user = session["user"]
    # session["data"] = {'A': 1, 'B': 1, 'C': 1, 'D': 1}
    return render_template("home.html", user=poll_user, openRooms=ROOMS)


@app.route('/joinRoom/', methods=["POST", "GET"])
def join_existing():
    return render_template("joinRoom.html")


@app.route('/user')
def user():
    poll_user = session["user"]
    return f"hello {poll_user}"


@app.route("/question/", methods=["POST", "GET"])
def question():
    if request.method == "POST":
        session['recentAns'] = request.form['ans']

        ans = session['recentAns']
        add_answers(ans)

        return redirect(url_for("results"))

    else:
        return render_template("submitAnswers.html")


"""
Creates a dictionary, data, in session if it does not already exist. 
Checks for the key in the dictionary that matches the param ans and increments its value. 
"""


def add_answers(ans):
    if "data" not in session:
        session["data"] = {'A': 0, 'B': 0, 'C': 0, 'D': 0}

    mydict = session["data"]

    for entry in mydict:
        if ans == entry:
            mydict[entry] += 1
    return mydict


@app.route("/results/")
def results():
    if "data" in session:
        data = session["data"]
        return render_template("resultsPage.html", data=data)
    else:
        redirect(url_for("question"))


@app.route("/room/<room_id>")
def poll_room(room_id):
    print(room_id)
    return render_template("pollRoom.html", room=ROOMS[room_id])

@socketio.on('create')
def on_create(data):
    if data['room_id'] in ROOMS:
        emit('error', {'error': 'Room With That ID Already Exists.'})
    else:
        pr = PollRoom(data['owner'], data['room_id'])
        rm_id = pr.roomID
        ROOMS.update({rm_id: pr})
        emit('join', {'id': rm_id})
        emit('redirect', {'url': url_for("poll_room", room_id=rm_id)})


@socketio.on('join')
def on_join(data):
    room = data['id']
    if room in ROOMS:
        join_room(room)
        emit('redirect', {'url': url_for("poll_room", room_id=room)})
    else:
        emit('error', {'error': 'Room does not exist.'})


if __name__ == '__main__':
    # app.run(debug=True)
    socketio.run(app, debug=True)
