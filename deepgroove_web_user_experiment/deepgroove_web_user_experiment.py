"""Main WEB interface definition module."""

from tempfile import NamedTemporaryFile
from pathlib import Path

from flask import render_template, request, session, redirect, url_for

from .training_interface import run_train, generate_clip
from . import APP

# TODO : Update with final values (remove divider)
TOTAL_TRIALS = 200 / 10
FINAL_TOTAL_TRIALS = 120 / 10


@APP.route("/", methods=['GET', 'POST'])
def register():
    """
    Greet the user and get the username for this session.

    When POSTed, redirects to the first trials.

    If the user already has entered his name, we skip this page and redirect to
    the trials. If the user wants to reset his session, he can simply access
    the /logout route which will clear his session.
    """

    # Respond to users information
    # ----------------------------
    if request.method == 'POST':
        session.permanent = True  # Make the cookies survive a browser shutdown
        session['participant_name'] = request.form['participant_name']
        APP.logger.info("participant name %s", session['participant_name'])
        APP.logger.info("Resetting ratings table")
        session['ratings_table'] = {}
        session.modified = True
        return redirect(url_for('trial'))

    # Otherwise: Display landing page
    # -------------------------------
    if 'participant_name' not in session:
        APP.logger.info("Creating initial landing page")
        return render_template('landing.html')

    APP.logger.info("User already has registered, so we direct him to trials")
    return redirect(url_for('trial'))


@APP.route("/logout")
def logout():
    """
    Reset the user's session so that we can restart with a clean slate.

    Visiting this page redirects to the landing page.
    """

    session.clear()
    return redirect(url_for('register'))


@APP.route("/trial", methods=['GET', 'POST'])
def trial():
    """
    Submit an experiment to the user and handle the responses.

    This function is where most of the logic of this WEB application resides.

    Entering this page calls the method to generate a new audio clip. This clip
    can be played over multiple times.

    When the user gives a rating for the clip, the results are posted to this
    page through the POST method and the page is reloaded, thus creating a new
    trial.
    """

    # Depending if we are in the final evaluation or not...
    if 'initial_ratings' not in session:
        max_trials = TOTAL_TRIALS
        step_name = 'Step 2/4: Data Gathering'
    else:
        max_trials = FINAL_TOTAL_TRIALS
        step_name = 'Step 4/4: Final Evaluation'

    # Handle the users response (POSTing)
    # -----------------------------------
    if request.method == 'POST':
        rating = request.form['rating']
        APP.logger.debug("Form is %s", request.form)
        clip_id = request.form['id']
        APP.logger.debug("user said %s of %s", rating, clip_id)
        session['ratings_table'][clip_id] = rating

        # We need this to trickle the modification to the proxy's target
        # object.
        session.modified = True

        # Only trigger the training if we are not in the final evaluation.
        if 'initial_ratings' not in session:
            run_train(session['ratings_table'])

        trial_count = len(session['ratings_table'].keys())

        # The user has not finished his trials yet, so supply a new one.
        if trial_count < max_trials:
            return redirect(url_for('trial'))

        # Otherwise the user has finished his trials. So redirect to the
        # appropriate page depending on his progress.
        # The user still has work to do.
        if 'initial_ratings' not in session:
            return redirect(url_for("train_wait"))

        # Otherwise, the user is all done !
        return redirect(url_for('finished'))

    # Otherwise, present the user with a new trial.
    # ---------------------------------------------
    prefix = Path(APP.static_folder, 'clips')
    clip_f = NamedTemporaryFile(
        dir=prefix.absolute().as_posix(),
        suffix='.wav',
        delete=False
    )
    clip_path = Path(clip_f.name)  # Reuse the tempfile name created by the OS
    APP.logger.debug("Path prefix is %s", prefix)
    APP.logger.debug("Clip filename is %s", clip_path.name)
    APP.logger.debug("clip path is %s", clip_path)

    clip_id = generate_clip(clip_path)
    APP.logger.debug("ratings table is now %s", session['ratings_table'])
    trial_count = "%s / %i" % (len(session['ratings_table'].keys()), max_trials)
    APP.logger.debug("trial count is %s", trial_count)

    # TODO : Consider keeping all the references to temporary files so we can
    # clean them up once all done.

    clip_url = url_for('static', filename='clips/' + clip_path.name)
    return render_template(
        'trial.html',
        step_name=step_name,
        clip_id=clip_id,
        clip_url=clip_url,
        trial=trial_count
    )


@APP.route("/train_wait")
def train_wait():
    """
    Display page informing user that the system is training.
    """

    return render_template('train_wait.html')


@APP.route("/final")
def final():
    """
    Final model evaluation by user.
    """
    session['initial_ratings'] = session.pop('ratings_table')
    session['ratings_table'] = {}
    return redirect(url_for('trial'))


@APP.route("/finished")
def finished():
    """
    Display a thank you note to the user.

    We could offer a bit of bling, e.g. :

       - Download all liked loops.
       - Show statistics,
       - etc.
    """

    return render_template('finished.html')
