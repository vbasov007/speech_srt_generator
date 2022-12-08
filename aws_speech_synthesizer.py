import json
import boto3
from utils import text_to_ssml, speech_marks_to_srt, text_to_ssml_advanced


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

    def synthesize(self, text, mp3_out=None, srt_out=None):

        ssml = text_to_ssml_advanced(text)

        print(ssml)

        if mp3_out is not None:
            response = self.client.synthesize_speech(Engine=self.engine,
                                                     VoiceId=self.voice_id,
                                                     OutputFormat='mp3',
                                                     TextType='ssml',
                                                     LanguageCode = self.language_code,
                                                     Text=ssml
                                                     )
            mp3_out.write(response['AudioStream'].read())


        if srt_out is not None:
            response = self.client.synthesize_speech(Engine=self.engine,
                                                     VoiceId=self.voice_id,
                                                     OutputFormat='json',
                                                     SpeechMarkTypes=['sentence'],
                                                     TextType='ssml',
                                                     LanguageCode=self.language_code,
                                                     Text=ssml
                                                     )

            sm_json = response['AudioStream'].read().decode('utf-8').split('\n')
            speech_marks_list = [json.loads(r) for r in sm_json if len(r) > 2]
            srt = speech_marks_to_srt(speech_marks_list)
            srt_out.write(srt)
