"""Main WEB interface definition module."""

from tempfile import NamedTemporaryFile
from pathlib import Path

from flask import render_template, request, session, redirect, url_for

from .training_interface import run_train, generate_clip
from . import APP

TOTAL_TRIALS = 200

@APP.route("/", methods=['GET', 'POST'])
def register():
    """
    Greet the user and get the username for this session.
    When POSTed, redirects to the first trials.
    """
    if request.method == 'POST':
        session.permanent = True
        session['participant_name'] = request.form['participant_name']
        APP.logger.info("participant name %s", session['participant_name'])
        APP.logger.info("Resetting ratings table")
        session['ratings_table'] = {}
        return redirect(url_for('trial'))

    if 'participant_name' not in session:
        APP.logger.info("Creating initial landing page")
        return render_template('landing.html')

    APP.logger.info("User already has registered, so we direct him to his trials")
    return redirect(url_for('trial'))


@APP.route("/trial", methods=['GET', 'POST'])
def trial():
    """
    Submit and experiment to the user.

    Entering this page calls the method to generate a new audio clip. This clip
    can be player over multiple times. When the user votes on the clip, the
    page is reloaded, thus creating a new clip.
    """
    if request.method == 'POST':
        rating = request.form['action']
        APP.logger.debug("Form is %s", request.form)
        clip_id = request.form['id']
        APP.logger.debug("user said %s of %s", rating, clip_id)
        session['ratings_table'][clip_id] = rating
        run_train(session['ratings_table'])
        session.modified = True
        step = len(session['ratings_table'].keys())
        if step < TOTAL_TRIALS:
            return redirect(url_for('trial'))
        return redirect(url_for("train_wait"))

    prefix = Path(APP.static_folder)
    clip_f = NamedTemporaryFile(dir=prefix.absolute().as_posix(),
                                suffix='.wav', delete=False)
    clip_path = Path(clip_f.name)
    APP.logger.debug("clip path is %s", clip_path)
    clip_id = generate_clip(clip_path)
    APP.logger.debug("ratings table is now %s", session['ratings_table'])
    step = "%s / %s" % (len(session['ratings_table'].keys()), TOTAL_TRIALS)
    APP.logger.debug("step is %s", step)
    clip_url = url_for('static', filename=clip_path.name)
    return render_template('trial.html',
                           clip_id=clip_id,
                           clip_url=clip_url,
                           step=step)


@APP.route("/train_wait")
def train_wait():
    """
    Display page informing user that the system is training.
    """
    return render_template('train_wait.html')
