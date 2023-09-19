import json

import boto3

from utils.misc_utils import speech_marks_to_srt, text_to_ssml

from mylogger import mylog


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
        mylog.info(f'Sending request to aws polly for synthesizing mp3: {len(ssml)} symbols')
        response = self.client.synthesize_speech(Engine=self.engine,
                                                 VoiceId=self.voice_id,
                                                 OutputFormat='mp3',
                                                 SampleRate='24000',
                                                 TextType='ssml',
                                                 LanguageCode=self.language_code,
                                                 Text=ssml
                                                 )
        mylog.info('Received response for synthesizing mp3')
        return response['AudioStream'].read()

    def synth_speech_marks(self, ssml):
        mylog.info(f'Sending request to aws polly for synthesizing json: {len(ssml)} symbols')
        response = self.client.synthesize_speech(Engine=self.engine,
                                                 VoiceId=self.voice_id,
                                                 OutputFormat='json',
                                                 SpeechMarkTypes=['sentence', 'ssml'],
                                                 TextType='ssml',
                                                 LanguageCode=self.language_code,
                                                 Text=ssml
                                                 )
        mylog.info('Received response for synthesizing json')
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

    def start_sentence_timings(self, ssml):
        speech_marks = self.synth_speech_marks(ssml)
        res = []
        for sm in speech_marks:
            if sm['type'] == 'sentence':
                res.append(int(sm['time']))

        return res