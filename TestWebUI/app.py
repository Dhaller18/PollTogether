

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

#for some reason, the dictionary gets passed, but the arguments aren't used properly by the pie chart script.
#they are properly used when the dictionary is freshly created within the same method before being sent to the .html
#As far as I can tell, this only happens with the dictionary
        return render_template("resultsPage.html", data=mydict)

    else:
        return render_template("submitAnswers.html")


def addAnswers(ans):
    if "data" not in session:
        session["data"] = {'A': 1, 'B': 1, 'C': 1, 'D': 1}

    mydict = session["data"]

    for entry in mydict:
        if ans == entry:
            mydict[entry] += 1
    return mydict


@app.route("/results/")
def results():
    # ans = session['user']
    # data = session['data']
    # return render_template("resultsPage.html", answer=ans, data=data)
    if "data" in session:
        ans = session['recentAns']
        data = session["data"]
        return render_template("resultsPage.html", data=data)
    else:
        redirect(url_for("question"))


if __name__ == '__main__':
    app.run(debug=True)
