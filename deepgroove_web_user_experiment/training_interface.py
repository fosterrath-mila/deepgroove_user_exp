"""
Interface code for WEB UI and training setup.
"""

import os
from pathlib import Path
from uuid import uuid4
from . import APP

import numpy as np
# TODO: import DeepDrummer


class Experiment:
    """
    Manage one deepdrummer experiment
    """

    def __init__(self, user_name):
        print('*** CREATING EXPERIMENT ***')

        self.user_name = user_name

        self.ratings_phase1 = {}

        self.ratings_phase2 = {}

        # TODO: create a new, untrained, freshly initialized model
        #self.model =







    def gen_clip(self, out_file_path):
        """
        Create audio and fill in audio specified WAV file.

        :param out_file_path: Path to the WAV which should be filled.
        :returns: The identifier of the clip.
        :rtype: str
        """

        # As a placeholder we are only now reading a static file and returning a
        # bytestream..
        dumb_audio_path = Path('./deepgroove_web_user_experiment/static/clips/trumpet-1.wav')
        APP.logger.warning(
            "Using stub data for audio generation from file %s",
           dumb_audio_path.absolute()
        )
        wav_data = dumb_audio_path.read_bytes()

        out_file_path = Path(out_file_path)
        APP.logger.debug("Placing audio data into file %s", out_file_path)
        out_file_path.write_bytes(wav_data)

        # TODO : Create WAV file for the generated audio having these parameters:
        # (use wave standard library module)
        # samplerate = 44100
        # nb_channels = 1
        # bit_depth = 16

        # TODO : Connect to the actual ID from the training setup
        clip_id = uuid4()

        return clip_id




    def add_rating_phase1(self, clip_uuid, rating):
        """
        Add a new rating for one clip
        """

        print('*** ADD RATING PHASE 1 ***')

        self.ratings_phase1[clip_uuid] = rating




    def add_rating_phase2(self, clip_uuid, rating):
        """
        Add a new rating for one clip
        """

        print('*** ADD RATING PHASE 2 ***')

        self.ratings_phase2[clip_uuid] = rating








    def train_incremental(self):
        """
        Do incremental retraining with additional ratings
        """

        print('*** INCREMENTAL RETRAINING ***')

        print('pid:', os.getpid())







    def full_retrain(self):
        """
        Run a complete retraiing from the available data. This happens
        during the pause and begins the second phase of the experiment.
        """

        print('*** FULL RETRAINING ***')





    def save_data(self):
        """
        Package and save the data from this experiment
        """

        print('*** SAVE EXPERIMENT DATA ***')
