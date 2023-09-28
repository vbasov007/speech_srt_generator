import boto3

import env

from  multilang import Translation

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
        return("Connection Successful")
    else:
        return("Connection Failed")

def test_translator():
    tr = Translation(env.environ['translator_url'],env.environ['translator_key'],
                     verify=env.environ['ignore_translator_ssl_cert'])

    try:
        res = tr.translate_text("Hi", target_lang="DE", source_lang="EN" )
    except Exception as e:
        return f"Failed: {str(e)}"

    return f"Success: Hi -> {res}"