"""Main module."""

from flask import Flask, render_template, request, session, redirect, url_for

APP = Flask(__name__)

APP.secret_key = b"1qaz2wsx42!000077777"

@APP.route("/", methods=['GET', 'POST'])
def register(username=None):
    """
    Greet the user and get the username for this session.
    """
    if request.method == 'POST':
        session['participant_name'] = request.form['participant_name']
        return redirect(url_for('trial'))
    else:
        return render_template('greetings.html')

@APP.route("/trial")
def trial():
    """
    Submit and experiment to the user.
    """
    return "Hello World"
