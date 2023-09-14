import os


def translator_url_key() -> (str, str):
    return os.environ.get('translator_url'), os.environ.get('translator_key')
