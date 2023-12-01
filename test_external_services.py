import os

import boto3

import env
from multilang import Translation


def test_polly():
    try:
        polly = boto3.Session(
            aws_access_key_id=env.environ['polly_key_id'],
            aws_secret_access_key=env.environ['polly_secret_key'],
            region_name=env.environ['polly_region']
        ).client('polly')
    except Exception as e:
        return f'Exception in session creation: {str(e)}'

    try:
        response = polly.synthesize_speech(
            OutputFormat='mp3',
            Text='Hello World',
            VoiceId='Joanna'
        )
    except Exception as e:
        return f'Exception in response: {str(e)}'

    if "AudioStream" in response:
        return ("Connection Successful")
    else:
        return ("Connection Failed")


def test_translator():
    tr = Translation(env.environ['translator_url'], env.environ['translator_key'],
                     verify=env.environ['ignore_translator_ssl_cert'])

    res=""
    try:
        res = tr.translate_text("Hi", target_lang="DE", source_lang="EN")
    except Exception as e:
        if len(res) > 0:
            return f"Success: Hi -> {res}, Warning: str(e)"
        return f"Error: {str(e)}"

    return f"Success: Hi -> {res}"


def check_folder_access(folder_path):
    if not os.path.exists(folder_path):
        return f"Directory does not exist."

    can_read = os.access(folder_path, os.R_OK)
    can_write = os.access(folder_path, os.W_OK)

    if can_read and can_write:
        return "Read Write"
    elif can_read:
        return "Read Only"
    elif can_write:
        return "Write Only"
    else:
        return "No Read, No Write"
