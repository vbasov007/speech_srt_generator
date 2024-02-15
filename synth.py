"""
Usage: synth.py [--config=CONFIG] [--srt=SRT] [--mp3=MP3] [--input=INPUT] [--out_folder=DATA_FOLDER]

Options:
  -h --help
  -c --config=CONFIG                    [default: config.yaml]
  -i --input=INPUT                      [default: input.txt]
  -s --srt=SRT                          [default: res.srt]
  -m --mp3=MP3                          [default: res.mp3]
  -f --out_folder=DATA_FOLDER           [default: output]
"""

import codecs
import os
from collections import namedtuple

import docopt
import yaml

from aws_speech_synthesizer import AwsSpeechSynthesizer
from utils.text2lines import text2lines, lines2ssml

ProviderConfig = namedtuple('ProviderConfig', ['access_key_id', 'secret_access_key', 'region'])
EngineConfig = namedtuple('EngineConfig', ['engine', 'voice_id', 'speech_style', 'language_code'])


class ArgsParser:
    def __init__(self, args):
        self.args = args
        self._yaml_cfg = None

    def _config(self):
        if self._yaml_cfg is None:
            with open(self.args.get('--config', 'default.yaml'), 'r') as yaml_file:
                yaml_doc = yaml_file.read()
            self._yaml_cfg = yaml.load(yaml_doc, Loader=yaml.FullLoader)
        return self._yaml_cfg

    @property
    def provider(self):
        c = self._config().get('provider')

        access_key_id = c.get('access_key_id', os.environ.get('polly_key_id'))
        secret_access_key = c.get('secret_access_key', os.environ.get('polly_secret_key'))

        return ProviderConfig(access_key_id=access_key_id,
                              secret_access_key=secret_access_key,
                              region=c['region'])

    @property
    def engine(self):
        c = self._config()['voice_engine']
        return EngineConfig(engine=c.get('engine', 'standard'),
                            voice_id=c.get('voice_id', 'Joanna'),
                            speech_style=c.get('speech_style', None),
                            language_code=c.get('language_code', 'en-US'))

    @property
    def translator_key(self):
        return self._config().get('translator_key', os.environ.get('translator_key'))

    @property
    def ignore_translator_ssl_cert(self):
        return os.environ.get('ignore_translator_ssl_cert', False)

    @property
    def output_folder(self):
        return self.args.get('--out_folder', '')

    def _path(self, file_name):
        return os.path.join(self.output_folder, file_name)

    @property
    def input_text(self):
        with open(self.args.get('--input'), encoding='utf-8', mode='r') as text:
            return str(text.read())

    @property
    def srt_file_path(self):
        return self._path(self.args.get('--srt'))

    @property
    def mp3_file_path(self):
        return self._path(self.args.get('--mp3'))


def converter(args, text=None, output_folder=None, mp3_file=None, srt_file=None, voice_id=None, language_code=None):
    cfg = ArgsParser(args)

    error_log = []

    voice_id = cfg.engine.voice_id if voice_id is None else voice_id
    language_code = cfg.engine.language_code if language_code is None else language_code

    synth = AwsSpeechSynthesizer(access_key_id=cfg.provider.access_key_id,
                                 secret_access_key=cfg.provider.secret_access_key,
                                 region_name=cfg.provider.region,
                                 engine=cfg.engine.engine,
                                 voice_id=voice_id,
                                 speech_style=cfg.engine.speech_style,
                                 language_code=language_code,
                                 )

    output_folder = cfg.output_folder if output_folder is None else output_folder
    mp3_file_path = cfg.mp3_file_path if mp3_file is None else os.path.join(output_folder, mp3_file)
    srt_file_path = cfg.srt_file_path if srt_file is None else os.path.join(output_folder, srt_file)

    if text is not None:
        input_text = text
    else:
        input_text = cfg.input_text

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(mp3_file_path, 'wb') as mp3_out, open(srt_file_path, 'w', encoding='utf-8') as srt_out:
        lines = text2lines(input_text)

        for line in lines:
            if line.type == 'sentence':
                try:
                    line.time_to_next = synth.duration(line.value)
                    print(f'{line.value} - {line.time_to_next}')
                except Exception:
                    error_log.append(f'{line.value}')

        if error_log:
            return error_log

        ssml = lines2ssml(lines)
        srt_out.write(codecs.BOM_UTF8.decode('utf-8'))
        synth.synth_speech_and_subtitles_to_files(text=ssml, mp3_out=mp3_out, srt_out=srt_out, ssml_input=True)


def main():
    args = docopt.docopt(__doc__)
    print(args)
    converter(args)


if __name__ == '__main__':
    main()
