#!/usr/bin/env bash

source env36/bin/activate

export MKL_NUM_THREADS=4
export NUMEXPR_NUM_THREADS=4
export OMP_NUM_THREADS=4

export FLASK_DEBUG=1
export FLASK_APP=deepgroove_web_user_experiment.deepgroove_web_user_experiment
flask run --host=0.0.0.0
