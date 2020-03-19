"""
Interface code for WEB UI and training setup.
"""

# from wave import open as wav_open
from logging import getLogger
from pathlib import Path
from uuid import uuid4

def generate_clip(out_file_path):
    """
    Create audio and fill in audio specified WAV file.

    :param out_file_path: Path to the WAV which should be filled.
    :returns: The identifier of the clip.
    :rtype: str
    """
    logger = getLogger(__name__)
    # As a placeholder we are only now reading a static file and returning a
    # bytestream..
    dumb_audio_path = Path('static/trumpet-1.wav')
    logger.warning("Using stub data for audio generation from file %s",
                   dumb_audio_path)
    wav_data = dumb_audio_path.read_bytes()

    out_file_path = Path(out_file_path)
    logger.debug("Placing audio data into file %s", out_file_path)
    out_file_path.write_bytes(wav_data)

    # TODO : Create WAV file for the generated audio having these parameters:
    # (use wave standard library module)
    # samplerate = 44100
    # nb_channels = 1
    # bit_depth = 16

    # TODO : Connect to the actual ID from the training setup
    clip_id = uuid4()

    return clip_id


def run_train(ratings):
    """
    This launches the training algorith with a (possibly) updated ratings table.
    """
    logger = getLogger(__name__)
    logger.debug("processing user submitted ratings : %s", ratings)
    # TODO : Use a process pool with shared object for training.
