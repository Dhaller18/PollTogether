from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "hello"


@app.route('/')
def home():
    session["user"] = "I am a user"
    user = session["user"]
    # session["data"] = {'A': 1, 'B': 1, 'C': 1, 'D': 1}
    return render_template("home.html", user=user)


@app.route('/user')
def user():
    user = session["user"]
    return f"hello {user}"


@app.route("/question/", methods=["POST", "GET"])
def question():
    if request.method == "POST":
        session['recentAns'] = request.form['ans']

        ans = session['recentAns']
        mydict = addAnswers(ans)

        return render_template("resultsPage.html", data=mydict)

    else:
        return render_template("submitAnswers.html")

"""
Creates a dictionary, data, in session if it does not already exist. 
Checks for the key in the dictionary that matches the param ans and increments its value. 
"""
def addAnswers(ans):
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


if __name__ == '__main__':
    app.run(debug=True)
