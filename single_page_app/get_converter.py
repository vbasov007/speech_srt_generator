from env import environ
from mp3_srt_synth import Mp3SrtSynth


def get_converter():
    return Mp3SrtSynth(access_key_id=environ.get('polly_key_id'),
                       secret_access_key=environ.get('polly_secret_key'),
                       region=environ.get('polly_region'),
                       )
