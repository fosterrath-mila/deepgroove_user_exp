"""
Interface code for WEB UI and training setup.
"""

import sys
import time
from pathlib import Path
from uuid import uuid4
from multiprocessing import Process, Queue, Pipe
import numpy as np
import soundfile as sf
from deepgroove.deepdrummer.experiment import Experiment
from . import APP

# Map of user indices to experiment objects
experiments = {}

def train_process(pipe, queue, exp_kwargs):
    """
    Training process. Communicates through a bidirectional pipe
    to receive commands and a queue to send audio clips.
    """

    # Create the experiment object
    experiment = Experiment(**exp_kwargs)

    while True:
        # If no incoming request and the queue is not full
        if experiment.phase == 1 and not pipe.poll() and not queue.full():
            print('Training')
            experiment.train_incremental()
            clip = experiment.gen_clip_phase1()
            queue.put(clip)
            continue

        print('Receiving message')

        # Read the message
        req = pipe.recv()
        req_type = req[0]
        args = req[1:]

        last_msg = time.time()

        print('got request: ', req)
        sys.stdout.flush()

        if req_type == 'ping':
            continue

        if req_type == 'add_rating':
            print('got rating')
            sys.stdout.flush()

            if experiment.phase == 1:
                experiment.add_rating_phase1(args[0], args[1])
            else:
                experiment.add_rating_phase2(args[0])
            continue

        if req_type == 'gen_clip':
            assert experiment.phase == 2
            clip = experiment.gen_clip_phase2()
            pipe.send(clip)

        if req_type == 'start_phase2':
            print('received start of phase 2')
            experiment.start_phase2()
            continue

        if req_type == 'save_data':
            save_path = args[0]
            data = experiment.save_data(save_path)
            pipe.send(data)
            break

        if req_type == 'close':
            break

        assert False, "unknown request type " + req[0]


class WebExperiment():
    """
    Handle web-specific details of experiment management
    """

    def __init__(self, **kwargs):
        self.phase = 1

        self.pipe, pipe_child = Pipe()

        self.queue = Queue(maxsize=20)

        self.proc = Process(target=train_process, kwargs={
            'pipe': pipe_child,
            'queue': self.queue,
            'exp_kwargs': kwargs
        })

        self.proc.start()

        self.last_audio = None
        self.last_clip_id = None

    def __del__(self):
        """
        Kill the process when deleting the experiment object
        """

        print('**** DELETING EXPERIMENT OBJECT ****')

        self.pipe.send(['close'])
        self.pipe.close()
        self.proc.join()

    @property
    def is_running(self):
        """
        Check if the training process is still running
        """

        try:
            self.pipe.send(['ping'])
        except IOError as e:
            return False

        return True

    def gen_clip(self, out_file_path):
        """
        Create audio and fill in audio specified WAV file.

        :param out_file_path: Path to the WAV which should be filled.
        :returns: The identifier of the clip.
        :rtype: str
        """

        if self.phase == 1:
            # Get the latest generated clip
            audio = self.queue.get()
            while not self.queue.empty():
                audio = self.queue.get()
        else:
            # Generate an audio clip
            self.pipe.send(['gen_clip'])
            audio = self.pipe.recv()

        out_file_path = Path(out_file_path)
        APP.logger.debug("Placing audio data into file %s", out_file_path)
        sf.write(out_file_path, audio, 44100)

        self.last_audio = audio
        self.last_clip_id = uuid4()

        return self.last_clip_id

    def add_rating(self, clip_uuid, rating):
        # In the web (async) case we want to prevent double submissions
        if str(clip_uuid) != str(self.last_clip_id):
            raise KeyError('mismatched clip uuid')

        # Send the rating to the training process
        self.pipe.send(['add_rating', rating, self.last_audio])

    def start_phase2(self):
        """
        Signal the start of phase 2
        """

        self.pipe.send(['start_phase2'])
        self.phase = 2

    def save_data(self, out_path):
        """
        Save the experiment data
        """

        self.pipe.send(['save_data', out_path])
        data = self.pipe.recv()
        return data
