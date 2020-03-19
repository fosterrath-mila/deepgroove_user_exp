"""Main WEB interface definition module."""

from flask import Flask, render_template, request, session, redirect, url_for
from logging import getLogger, basicConfig, DEBUG

basicConfig(level=DEBUG)

APP = Flask(__name__)
APP.secret_key = b"1qaz2wsx42!000077777"


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
        return redirect(url_for('trial'))

    return render_template('greetings.html')


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
        # TODO : Here we need to connect with a given ID for the sample.
        vote = request.form['action']
        # TODO : Call feedback function to model.
        logger.debug("user voted %s", vote)
        return redirect(url_for('trial'))
    else:
        session['clip_path'] = url_for('static', filename='trumpet-1.wav')
        return render_template('trial.html')
