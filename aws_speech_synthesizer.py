import json

import boto3

from utils import speech_marks_to_srt, text_to_ssml, remove_all_tags


class AwsSpeechSynthesizer:
    def __init__(self, **kwargs):
        self.engine = kwargs.get('engine', 'standard')
        self.voice_id = kwargs.get('voice_id', '')
        self.access_key_id = kwargs.get('access_key_id', '')
        self.secret_access_key = kwargs.get('secret_access_key', '')
        self.region_name = kwargs.get('region_name', '')
        self.speech_style = kwargs.get('speech_style', None)
        self.language_code = kwargs.get('language_code', 'en-US')

        session = boto3.Session(aws_access_key_id=self.access_key_id,
                                aws_secret_access_key=self.secret_access_key,
                                region_name=self.region_name)
        self.client = session.client('polly')

    def synth_mp3(self, ssml):
        response = self.client.synthesize_speech(Engine=self.engine,
                                                 VoiceId=self.voice_id,
                                                 OutputFormat='mp3',
                                                 SampleRate='24000',
                                                 TextType='ssml',
                                                 LanguageCode=self.language_code,
                                                 Text=ssml
                                                 )
        return response['AudioStream'].read()

    def synth_speech_marks(self, ssml):
        response = self.client.synthesize_speech(Engine=self.engine,
                                                 VoiceId=self.voice_id,
                                                 OutputFormat='json',
                                                 SpeechMarkTypes=['sentence', 'ssml'],
                                                 TextType='ssml',
                                                 LanguageCode=self.language_code,
                                                 Text=ssml
                                                 )
        sm_json = response['AudioStream'].read().decode('utf-8').split('\n')
        speech_marks_list = [json.loads(r) for r in sm_json if r != '']
        return speech_marks_list

    def synthesize(self, text, mp3_out=None, srt_out=None, ssml_input=False):

        ssml = text if ssml_input else text_to_ssml(text)

        if mp3_out is not None:
            response = self.synth_mp3(ssml)
            mp3_out.write(response)

        if srt_out is not None:
            srt = speech_marks_to_srt(self.synth_speech_marks(ssml), srt_out)
            srt_out.write(srt)

    def duration(self, frase):
        speech_marks = self.synth_speech_marks(f'<speak> {frase} <mark name="end"/></speak>')
        for sm in speech_marks:
            if sm['type'] == 'ssml' and sm['value'] == 'end':
                return int(sm['time'])
        return None