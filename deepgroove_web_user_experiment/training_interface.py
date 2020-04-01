"""
Interface code for WEB UI and training setup.
"""

import os
from pathlib import Path
from uuid import uuid4
from . import APP

import soundfile as sf
from deepgroove.deepdrummer.experiment import Experiment

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
