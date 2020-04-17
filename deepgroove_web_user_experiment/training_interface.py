"""
Interface code for WEB UI and training setup.
"""

import sys
from pathlib import Path
from uuid import uuid4
from multiprocessing import Process, Queue, Pipe
import numpy as np
import soundfile as sf
from deepgroove.deepdrummer.experiment import Experiment
from . import APP

# Map of user indices to experiment objects
experiments = {}

def train_process(pipe, user_name, user_email):
    """
    Training process. Communicates through a bidirectional pipe
    """

    # Create the experiment object
    experiment = Experiment(user_email, user_name)

    # Keep track of the current phase
    phase = 1

    # Latest clip generated during phase 1
    latest_clip = experiment.gen_clip_phase1()

    # FIXME: we need some kind of a timeout
    # at least stop training if we haven't received any ratings/requests in a while.

    while True:
        if not pipe.poll() and phase == 1:
            print('Training')
            experiment.train_incremental()
            latest_clip = experiment.gen_clip_phase1()
            continue

        print('Receiving message')

        # Read the message
        req = pipe.recv()
        req_type = req[0]
        args = req[1:]

        print('got request: ', req)
        sys.stdout.flush()

        if req_type == 'add_rating':
            print('got rating')
            sys.stdout.flush()

            if phase is 1:
                experiment.add_rating_phase1(args[0])
            else:
                experiment.add_rating_phase2(args[0])
            continue

        if req_type == 'gen_clip':
            if phase is 1:
                print('sending clip')
                pipe.send(latest_clip)
                print('clip sent')
            else:
                clip = experiment.gen_clip_phase2()
                pipe.send(clip)
            continue

        if req_type == 'start_phase2':
            print('received start of phase 2')
            experiment.start_phase2()
            phase = 2
            continue

        assert False, "unknown request type " + req[0]


class WebExperiment():
    """
    Handle web-specific details of experiment management
    """

    def __init__(self, user_email, user_name):

        self.pipe, pipe_child = Pipe()

        self.proc = Process(target=train_process, kwargs={
            'pipe': pipe_child,
            'user_email': user_email,
            'user_name': user_name
        })

        self.proc.start()

        self.last_clip_id = None

    def __del__(self):
        """
        Kill the process when deleting the experiment object
        """

        print('**** DELETING EXPERIMENT OBJECT ****')

        self.reqs.send(['close'])
        self.reqs.close()
        self.resp.close()
        self.proc.join()

    def gen_clip(self, out_file_path):
        """
        Create audio and fill in audio specified WAV file.

        :param out_file_path: Path to the WAV which should be filled.
        :returns: The identifier of the clip.
        :rtype: str
        """

        # Generate an audio clip
        self.pipe.send(['gen_clip'])
        audio = self.pipe.recv()

        out_file_path = Path(out_file_path)
        APP.logger.debug("Placing audio data into file %s", out_file_path)
        sf.write(out_file_path, audio, 44100)

        self.last_clip_id = uuid4()

        return self.last_clip_id

    def add_rating(self, clip_uuid, rating):
        # In the web (async) case we want to prevent double submissions
        if str(clip_uuid) != str(self.last_clip_id):
            raise KeyError('mismatched clip uuid')

        # Send the rating to the training process
        self.pipe.send(['add_rating', rating])

    def start_phase2(self):
        """
        Signal the start of phase 2
        """

        self.pipe.send(['start_phase2'])

    def save_data(self, out_path):
        """
        Save the experiment data
        """

        # TODO
        pass
