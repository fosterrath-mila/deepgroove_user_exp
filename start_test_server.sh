#!/usr/bin/env bash

source env36/bin/activate
export FLASK_DEBUG=1
export FLASK_APP=deepgroove_web_user_experiment.deepgroove_web_user_experiment
flask run
