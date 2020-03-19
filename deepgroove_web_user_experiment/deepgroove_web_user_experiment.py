"""Main WEB interface definition module."""

from tempfile import NamedTemporaryFile
from logging import getLogger
from pathlib import Path

from flask import render_template, request, session, redirect, url_for

from .training_interface import run_train, generate_clip
from . import APP

# TODO : State machine, implement steps

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
        clip_id = request.form['id']
        logger.debug("user said %s of %s", rating, clip_id)
        session['ratings_table'][rating] = clip_id
        run_train(session['ratings_table'])
        return redirect(url_for('trial'))

    # TODO : Here we should generate the temporary file with a prefix for the generated files.
    clip_f = NamedTemporaryFile(prefix='./static/', delete=False)
    clip_path = Path(clip_f.name)
    clip_id = generate_clip(clip_path)
    # TODO : Generate a unique UUID for the file.
    clip_url = url_for('static', filename=clip_path.stem)
    return render_template('trial.html', clip_url=clip_url, clip_id=clip_id)
