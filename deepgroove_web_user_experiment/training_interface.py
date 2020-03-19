from pathlib import Path
from wave import open as wav_open

def generate_clip(filename):
    """
    Create audio and fill in audio WAV file.

    :param filename: Path to the WAV which should be filled.
    """
    # As a placeholder we are only now reading a static file and returning a
    # bytestream..
    audio_src = wav_open('static/trumpet-1.wav')

    # samplerate = 44100
    # nb_channels = 1
    # bit_depth = 16
    out_file = Path(filename)


def run_train(ratings):
    """
    This launches the training algorith with a (possibly) updated ratings table.
    """
    # TODO : Use a process pool with shared object for training.
    pass

