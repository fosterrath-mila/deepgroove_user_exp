"""
Interface code for WEB UI and training setup.
"""

import os
from pathlib import Path
from uuid import uuid4
from . import APP

import numpy as np
import soundfile as sf
# TODO: import DeepDrummer

class Experiment:
    """
    Manage one deepdrummer experiment
    """

    def __init__(self, user_name):
        print('*** CREATING EXPERIMENT ***')

        self.user_name = user_name

        self.ratings_phase1 = []

        self.ratings_phase2 = []

        # TODO: create a new, untrained, freshly initialized model
        #self.model =







    def gen_clip(self):
        """
        Create audio and fill in audio specified WAV file.

        :param out_file_path: Path to the WAV which should be filled.
        :returns: The identifier of the clip.
        :rtype: str
        """

        # TODO:
        # Generate audio using the model
        audio = np.zeros((44100*2, 1))










        return audio

    def add_rating_phase1(self, rating):
        """
        Add a new rating for one clip
        """

        print('*** ADD RATING PHASE 1 ***')

        self.ratings_phase1.append(rating)




    def add_rating_phase2(self, rating):
        """
        Add a new rating for one clip
        """

        print('*** ADD RATING PHASE 2 ***')

        self.ratings_phase2.append(rating)








    def train_incremental(self):
        """
        Do incremental retraining with additional ratings
        """

        print('*** INCREMENTAL RETRAINING ***')







    def full_retrain(self):
        """
        Run a complete retraiing from the available data. This happens
        during the pause and begins the second phase of the experiment.
        """

        print('*** FULL RETRAINING ***')





    def save_data(self):
        """
        Package and save the data from this experiment
        We want to save all audio and ratings
        """

        print('*** SAVE EXPERIMENT DATA ***')

        # TODO: figure out where we want to put the data






class WebExperiment(Experiment):
    """
    Handle web-specific details of experiment management
    """

    def __init__(self, user_name):
        super().__init__(user_name)

        self.last_clip_id = None

    def add_rating_phase1(self, clip_uuid, rating):
        # In the web (async) case we want to prevent double submissions
        if str(clip_uuid) != str(self.last_clip_id):
            raise KeyError('mismatched clip uuid')

        super().add_rating_phase1(rating)

    def add_rating_phase2(self, clip_uuid, rating):
        # In the web (async) case we want to prevent double submissions
        if str(clip_uuid) != str(self.last_clip_id):
            raise KeyError('mismatched clip uuid')

        super().add_rating_phase2(rating)

    def gen_clip(self, out_file_path):
        """
        Create audio and fill in audio specified WAV file.

        :param out_file_path: Path to the WAV which should be filled.
        :returns: The identifier of the clip.
        :rtype: str
        """

        audio = super().gen_clip()

        out_file_path = Path(out_file_path)
        APP.logger.debug("Placing audio data into file %s", out_file_path)
        sf.write(out_file_path, audio, 44100)

        self.last_clip_id = uuid4()

        return self.last_clip_id
