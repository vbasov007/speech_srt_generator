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

import docopt
import yaml
import os
from collections import namedtuple
from aws_speech_synthesizer import AwsSpeechSynthesizer

ProviderConfig = namedtuple('ProviderConfig', ['access_key_id', 'secret_access_key', 'region'])
EngineConfig = namedtuple('EngineConfig', ['engine', 'voice_id', 'speech_style'])


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
        c = self._config()['provider']
        return ProviderConfig(access_key_id=c['access_key_id'],
                              secret_access_key=c['secret_access_key'],
                              region=c['region'])

    @property
    def engine(self):
        c = self._config()['voice_engine']
        return EngineConfig(engine=c.get('engine', 'standard'),
                            voice_id=c.get('voice_id', 'Joanna'),
                            speech_style=c.get('speech_style', None))

    @property
    def output_folder(self):
        return self.args.get('--out_folder', '')

    def _path(self, file_name):
        return os.path.join(self.output_folder, file_name)

    @property
    def input_text(self):
        with open(self.args.get('--input'), 'r') as text:
            return str(text.read())

    @property
    def srt_file_path(self):
        return self._path(self.args.get('--srt'))

    @property
    def mp3_file_path(self):
        return self._path(self.args.get('--mp3'))


def main():
    cfg = ArgsParser(docopt.docopt(__doc__))

    synth = AwsSpeechSynthesizer(access_key_id=cfg.provider.access_key_id,
                                 secret_access_key=cfg.provider.secret_access_key,
                                 region_name=cfg.provider.region,
                                 engine=cfg.engine.engine,
                                 voice_id=cfg.engine.voice_id,
                                 speech_style=cfg.engine.speech_style,
                                 )

    if not os.path.exists(cfg.output_folder):
        os.makedirs(cfg.output_folder)

    with open(cfg.mp3_file_path, 'wb') as mp3_out, open(cfg.srt_file_path, 'w') as srt_out:
        synth.synthesize(text=cfg.input_text, mp3_out=mp3_out, srt_out=srt_out)


if __name__ == '__main__':
    main()
