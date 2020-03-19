"""Main WEB interface definition module."""

from flask import Flask, render_template, request, session, redirect, url_for
from logging import getLogger, basicConfig, DEBUG
from uuid import uuid4

basicConfig(level=DEBUG)

APP = Flask(__name__)
APP.secret_key = b"1qaz2wsx42!000077777"

# TODO : State machine
# TODO : Table de ratings
# TODO : Interface for call to training
# TODO : Use a process pool with shared object for training.

@APP.route("/", methods=['GET', 'POST'])
def register():
    """
    Greet the user and get the username for this session.
    When POSTed, redirects to the first trials.
    """
    logger = getLogger(__name__)
    if request.method == 'POST':
        session['participant_name'] = request.form['participant_name']
        logger.debug("participant name %s", session['participant_name'])
        session['ratings_table'] = {}
        return redirect(url_for('trial'))

    return render_template('landing.html')


@APP.route("/trial", methods=['GET', 'POST'])
def trial():
    """
    Submit and experiment to the user.

    Entering this page calls the method to generate a new audio clip. This clip
    can be player over multiple times. When the user votes on the clip, the
    page is reloaded, thus creating a new clip.
    """
    logger = getLogger(__name__)

    if request.method == 'POST':
        rating = request.form['action']
        session['ratings_table'][rating] = request.form['id']
        # TODO : Trigger model training
        logger.debug("user voted %s", vote)
        return redirect(url_for('trial'))

    # TODO : Here we should generate the temporary file with a prefix for the generated files.
    # TODO : Generate a unique UUID for the file.
    clip_url = url_for('static', filename='trumpet-1.wav')
    return render_template('trial.html', clip_url=clip_url)
