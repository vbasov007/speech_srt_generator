from typing import Optional

import boto3

from speech_synth_interface import SpeechChunk, SpeechSynthInterface
from utils import mp3_to_pcm


class AwsSpeechSynthesizer1(SpeechSynthInterface):
    def __init__(self, **kwargs):
        self.engine = kwargs.get('engine', 'standard')
        self.voice_id = kwargs.get('voice_id', '')
        self.access_key_id = kwargs.get('access_key_id', '')
        self.secret_access_key = kwargs.get("secret_access_key", '')
        self.region_name = kwargs.get('region_name', '')
        self.speech_style = kwargs.get('speech_style', None)
        self.language_code = kwargs.get('language_code', 'en-US')

        session = boto3.Session(aws_access_key_id=self.access_key_id,
                                aws_secret_access_key=self.secret_access_key,
                                region_name=self.region_name)
        self.client = session.client('polly')

    def synth(self, text: str,
              voice: str = "default",
              speech_style: str = "default",
              language_code: str = "default",
              text_type: str = "ssml",
              encoding: str = "LINEAR16",
              sample_rate_hz: Optional[int] = 24000,
              absolute_start_time_ms: Optional[int] = None) -> SpeechChunk:

        assert voice in ["default", self.voice_id], f'Voice "{voice}" not supported'
        assert speech_style in ["default", self.speech_style], f'Speech style "{speech_style}" not supported'
        assert language_code in ["default", self.language_code], f'Language "{language_code}" not supported'
        assert text_type in ["ssml", "text"], f'Text type "{text_type}" not supported'
        assert encoding in ["LINEAR16", ], f'Encoding "{text_type}" not supported'
        assert sample_rate_hz in [24000, ], f'Sample rate {text_type} Hz not supported'

        speech_chunk = self._get_speech_chunk_pcm(text)

        return SpeechChunk(stream=speech_chunk,
                           language_code=self.language_code,
                           duration_ms=int(len(bytes(speech_chunk)) * 500 / sample_rate_hz),
                           sample_rate_hz=sample_rate_hz,
                           encoding=encoding,
                           absolut_start_time_ms=absolute_start_time_ms)

    def _get_speech_chunk_pcm(self, ssml: str):
        response = self.client.synthesize_speech(Engine=self.engine,
                                                 VoiceId=self.voice_id,
                                                 OutputFormat="mp3",
                                                 SampleRate="24000",
                                                 TextType='ssml',
                                                 LanguageCode=self.language_code,
                                                 Text=f'<speak>{ssml}</speak>',
                                                 )
        return mp3_to_pcm(response['AudioStream'].read())[44:]
