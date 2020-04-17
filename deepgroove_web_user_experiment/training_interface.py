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

    while True:
        if not pipe.poll() and phase == 1:
            print('Training')
            experiment.train_incremental()
            latest_clip = experiment.gen_clip_phase1()
            continue

        print('pipe poll:', pipe.poll())

        req = pipe.recv()

        print('got request: ', req)
        sys.stdout.flush()

        if req[0] == 'add_rating':
            print('got rating')
            sys.stdout.flush()

            if phase is 1:
                experiment.add_rating_phase1(req[1])
            else:
                experiment.add_rating_phase2(req[1])
            continue

        if req[0] == 'get_clip':
            if phase is 1:
                print('sending clip')
                pipe.send(latest_clip)
                print('clip sent')
            else:
                assert False
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

        #audio = super().gen_clip_phase1()

        # Generate an audio clip
        self.pipe.send(['get_clip'])
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

        print('SENDING RATING')

        # Send the rating to the training process
        self.pipe.send(['add_rating', rating])
