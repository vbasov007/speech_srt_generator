import json

import boto3

from mylogger import mylog
from utils import mp3_to_pcm
from utils import write_as_mp3
from utils.misc_utils import speech_marks_to_srt, text_to_ssml
from utils.replace_xml_reserved_chars import unescape_xml_chars


def is_sentence(line: str):
    return line.startswith("<s>") and line.endswith("</s>")


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

    def _get_speech_chunk_pcm(self, ssml: str):
        response = self.client.synthesize_speech(Engine=self.engine,
                                                 VoiceId=self.voice_id,
                                                 OutputFormat="mp3",
                                                 SampleRate="24000",
                                                 TextType='ssml',
                                                 LanguageCode=self.language_code,
                                                 Text=f'<speak>{ssml}</speak>',
                                                 )
        return mp3_to_pcm(response['AudioStream'].read())

    def synth_speech_pcm_stream(self, ssml, max_sentences_per_batch: int = 10, sample_rate_hz: int = 24000):
        mylog.info(f'Sending request to aws polly for synthesizing speech pcm: {len(ssml)} symbols')

        streams = []
        batch_lines = []
        lines = ssml.split("\n")
        sentence_count = 0
        for i, line in enumerate(lines):
            batch_lines.append(line)
            if is_sentence(line):
                sentence_count += 1
            if sentence_count >= max_sentences_per_batch or (i == len(lines) - 1):
                if len(batch_lines) == 1:
                    batch_lines.append("")
                speech_marks = self._get_batch_speech_marks("\n".join(batch_lines))
                # remove 44 bytes of wav header
                speech_chunk = self._get_speech_chunk_pcm("\n".join(batch_lines[:-1]))[44:]
                target_chunk_duration_ms = int(speech_marks[-1]["time"])
                actual_duration_ms = int(len(bytes(speech_chunk)) * 500 / sample_rate_hz)
                addition = (target_chunk_duration_ms - actual_duration_ms) * sample_rate_hz
                if addition > 0:
                    speech_chunk += b'\x00\x00' * int(addition / 1000)

                streams.append(speech_chunk)
                batch_lines = [batch_lines[-1], ]
                sentence_count = 1

        return b''.join(streams)

    def _get_batch_speech_marks(self, ssml):
        response = self.client.synthesize_speech(Engine=self.engine,
                                                 VoiceId=self.voice_id,
                                                 OutputFormat='json',
                                                 SpeechMarkTypes=['sentence', 'ssml'],
                                                 TextType='ssml',
                                                 LanguageCode=self.language_code,
                                                 Text=f'<speak>{ssml}</speak>'
                                                 )
        sm_json = response['AudioStream'].read().decode('utf-8').split('\n')
        return [json.loads(r) for r in sm_json if r != '']

    def synth_speech_marks(self, ssml, max_sentences_per_batch=10):

        mylog.info(f'Sending request to aws polly for synthesizing json: {len(ssml)} symbols')

        lines = ssml.split("\n")

        sentence_count = 0
        batch_lines = []
        current_batch_start_time = 0
        next_batch_start_time = 0
        speech_marks_list_time_offset = []
        res = []
        for i, line in enumerate(lines):
            batch_lines.append(line)
            if is_sentence(line):
                sentence_count += 1
            if sentence_count >= max_sentences_per_batch or (i == len(lines) - 1):
                batch_ssml = "\n".join(batch_lines)

                speech_marks_list = self._get_batch_speech_marks(batch_ssml)

                speech_marks_list_time_offset = []
                for item in speech_marks_list:
                    if item['type'] == 'sentence':
                        item['time'] += current_batch_start_time
                        next_batch_start_time = item['time']
                    speech_marks_list_time_offset.append(item)
                current_batch_start_time = next_batch_start_time
                res.extend(speech_marks_list_time_offset[:-1])
                batch_lines = [batch_lines[-1], ]
                sentence_count = 1
        if speech_marks_list_time_offset:
            res.append(speech_marks_list_time_offset[-1])
        return res

    def synth_speech_and_subtitles_to_files(self, text, mp3_out=None, srt_out=None, ssml_input=False):

        ssml = text if ssml_input else text_to_ssml(text)

        if mp3_out is not None:
            response = self.synth_speech_pcm_stream(ssml)
            write_as_mp3(mp3_out, response)
            # mp3_out.write(response)

        if srt_out is not None:
            srt = speech_marks_to_srt(self.synth_speech_marks(ssml), srt_out)
            srt = unescape_xml_chars(srt)
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
