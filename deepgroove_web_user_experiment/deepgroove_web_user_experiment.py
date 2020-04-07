"""Main WEB interface definition module."""

import os
import csv
from logging import StreamHandler, INFO
from tempfile import NamedTemporaryFile
from pathlib import Path

from flask import render_template, request, session, redirect, url_for

from .training_interface import WebExperiment
from . import APP

# Divided by ten for development purposes.
TOTAL_TRIALS = 200 / 10
FINAL_TOTAL_TRIALS = 120 / 10

# Object to manage the state of the experiment (ie: model and data)
# We might want to consider storing the experiment in the context of the
# session. i.e.: The session is perenial to a user's context in the
# interactivity with all of the functions in this context. Because here, as a
# global variable there is a danger that variable instances be HTTP - worker
# local. And that could turn into a pretty clusterfuck. That being said, I
# doubdt that the session will handle the pickling of a custom class without
# pain. I'd go for state in the session object, and stateless functions in the
# training_interface.py module.
experiment = None


def find_user(query_email):
    """
    Locate a given user in the list based on their e-mail
    This produces their full name as well as a unique user index
    The user index is simply the row index in the spreadsheet, which
    we can use to identify the user internally.
    """

    csv_path = os.path.join(APP.root_path, 'user_list.csv')

    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        #rows = list(reader)

        for idx, row in enumerate(reader):
            # Skip the first row (heading)
            if idx == 0:
                continue

            user_email, user_name, status = row
            print(user_email, user_name, status)

            # Return the row number of the user
            if user_email == query_email:
                return idx, user_name, status

    raise KeyError('user not found')


@APP.before_first_request
def setup_logging():
    """
    We need to configure the logger before we acess it, or else it is non
    functionnal in a Flask production setting.
    """
    if not APP.debug:
        APP.logger.setLevel(INFO)


@APP.route("/", methods=['GET', 'POST'])
def register():
    """
    Greet the user and get the username for this session.

    When POSTed, redirects to the first trials.

    If the user already has entered his name, we skip this page and redirect to
    the trials. If the user wants to reset his session, he can simply access
    the /logout route which will clear his session.
    """

    global experiment

    if 'state' not in session:
        session['state'] = 'landing'

    # Respond to users information being submitted
    if request.method == 'POST':
        user_email = request.form['user_email']
        APP.logger.info("User e-mail %s", user_email)
        APP.logger.info("Resetting ratings table")

        try:
            # Find the user in the list
            user_idx, user_name, status = find_user(user_email)

        except KeyError:
            return render_template(
                'landing.html',
                error_string='ERROR: user not found, please make sure to use ' +
                'the same e-mail address you previously shared with us.'
            )

        session.permanent = True  # Make the cookies survive a browser shutdown
        session['user_idx'] = user_idx
        session['user_email'] = user_email
        session['user_name'] = user_name
        session['state'] = 'phase1'
        session.modified = True

        # Create the experiment object
        experiment = WebExperiment(user_email, user_name)

        return redirect(url_for('trial'))

    # If the user has already completed the experiment
    if session['state'] == 'finished':
        return redirect(url_for('finished'))

    # If the experiment is ongoing
    if session['state'] in ['phase1', 'phase2']:
        return redirect(url_for('trial'))

    APP.logger.info("Creating initial landing page")
    session.modified = True
    return render_template('landing.html')


@APP.route("/logout")
def logout():
    """
    Reset the user's session so that we can restart with a clean slate.

    Visiting this page redirects to the landing page.
    """

    global experiment

    session.clear()
    session.modified = True
    experiment = None
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

    global experiment

    # Depending if we are in the final evaluation or not...
    if session['state'] == 'phase1':
        step_name = 'Step 2/4: Data Gathering'
        trial_count = len(experiment.ratings_phase1)
        max_trials = TOTAL_TRIALS
    elif session['state'] == 'phase2':
        step_name = 'Step 4/4: Final Evaluation'
        trial_count = len(experiment.ratings_phase2)
        max_trials = FINAL_TOTAL_TRIALS
    else:
        assert False, 'invalid session state "{}"'.format(session['state'])

    # Handle the users response (POSTing)
    if request.method == 'POST':
        rating = request.form['rating']
        APP.logger.debug("Form is %s", request.form)
        clip_id = request.form['id']
        APP.logger.debug("user said %s of %s", rating, clip_id)

        # Only trigger the training if we are not in the final evaluation.
        if session['state'] == 'phase1':
            experiment.add_rating_phase1(clip_id, rating)
            experiment.train_incremental()
        else:
            experiment.add_rating_phase2(clip_id, rating)

        # The user has not finished his trials yet, so supply a new one.
        if trial_count + 1 < max_trials:
            return redirect(url_for('trial'))

        # Otherwise the user has finished his trials. So redirect to the
        # appropriate page depending on his progress.
        # The user still has work to do.
        if session['state'] == 'phase1':
            experiment.full_retrain()
            session['state'] = 'phase2'
            session.modified = True
            return redirect(url_for("train_wait"))

        # Otherwise, the user is all done !
        experiment.save_data()
        experiment = None
        session['state'] = 'finished'
        session.modified = True
        return redirect(url_for('finished'))

    # Otherwise, present the user with a new trial.
    prefix = Path(APP.static_folder, 'clips')
    clip_f = NamedTemporaryFile(
        dir=prefix.absolute().as_posix(),
        suffix='.wav',
        delete=False
    )
    clip_path = Path(clip_f.name)
    APP.logger.debug("clip path is %s", clip_path)

    if session['state'] == 'phase1':
        clip_id = experiment.gen_clip_phase1(clip_path)
    else:
        clip_id = experiment.gen_clip_phase2(clip_path)

    trial_count_str = "%s / %i" % (trial_count + 1, max_trials)
    APP.logger.debug("trial count is %s", trial_count_str)

    # TODO : Consider keeping all the references to temporary files so we can
    # clean them up once all done.
    print(prefix)
    print(clip_path.name)

    clip_url = url_for('static', filename='clips/' + clip_path.name)
    return render_template(
        'trial.html',
        step_name=step_name,
        clip_id=clip_id,
        clip_url=clip_url,
        trial=trial_count_str
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

    assert session['state'] == 'phase2'
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
