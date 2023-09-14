import codecs
from typing import List, Dict

from aws_speech_synthesizer import AwsSpeechSynthesizer
from utils.text2lines import text2lines, lines2ssml, ScriptLine

class Mp3SrtSynthException(Exception):
    pass

class Mp3SrtSynth:
    long_lang_code = {
        'EN': 'en-US',
        'DE': 'de-DE',
        'FR': 'fr-FR',
        # 'ES': 'es-ES',
        'IT': 'it-IT',
        # 'PL': 'pl-PL',
        # 'PT': 'pt-PT',
        # 'RU': 'ru-RU',
        'JA': 'ja-JP',
        'ZH': 'cmn-CN',
    }

    lang_code_to_name = {
        'EN': 'English',
        'DE': 'Deutsch',
        'FR': 'Français',
        # 'ES': 'Español',
        'IT': 'Italiano',
        # 'PL': 'Polski',
        # 'PT': 'Português'
        # 'RU': 'Русский',
        'JA': 'Japanese',
        'ZH': 'Chinese',
    }

    voices = {
        "EN": ["Matthew", "Joey", "Joanna", "Kendra"],
        "DE": ["Daniel","Vicki"],
        "FR": ["Lea", "Remi"],
        "IT": ["Bianca", "Adriano"],
        "ZH": ["Zhiyu",],
        "JA": ["Kazuha", "Takumi", "Tomoko"],
    }

    def __init__(self, access_key_id, secret_access_key, region, engine):
        self._access_key_id = access_key_id
        self._secret_access_key = secret_access_key
        self._region = region
        self._engine = engine
        self._synthesizers: Dict[str, AwsSpeechSynthesizer] = {}

    def add_lang(self, voice_id, short_lang_code, speech_style="conversational"):
        self._synthesizers[short_lang_code] = AwsSpeechSynthesizer(access_key_id=self._access_key_id,
                                                                   secret_access_key=self._secret_access_key,
                                                                   region_name=self._region,
                                                                   engine=self._engine,
                                                                   voice_id=voice_id,
                                                                   speech_style=speech_style,
                                                                   language_code=self.long_lang_code[short_lang_code],
                                                                   )

    def _calc_adjustments_old(self, translations: Dict[str, str]) -> Dict[str, List[ScriptLine]]:
        lines: Dict[str, List[ScriptLine]] = {}
        for short_lang_code, text in translations.items():
            lines[short_lang_code] = text2lines(text)
            for line in lines[short_lang_code]:
                if line.type == 'sentence':
                    line.duration = self._synthesizers[short_lang_code].duration(line.value)

        keys = list(lines.keys())
        for i, v in enumerate(zip(*lines.values())):
            if v[0].type != 'sentence':
                continue
            max_duration = max(x.duration for x in v)
            rs = [max_duration - x.duration for x in v]
            for l, r in zip(keys, rs):
                lines[l][i].adjustment = r

        return lines

    def _calc_adjustments(self, translations: Dict[str, str]) -> Dict[str, List[ScriptLine]]:
        lines: Dict[str, List[ScriptLine]] = {}
        sentences: Dict[str, List[ScriptLine]] = {}
        for short_lang_code, text in translations.items():
            lines[short_lang_code] = text2lines(text)
            ssml = lines2ssml(lines[short_lang_code])
            timings = self._synthesizers[short_lang_code].start_sentence_timings(ssml)
            sentences[short_lang_code] = [x for x in lines[short_lang_code] if x.type == 'sentence']
            for i in range(len(sentences[short_lang_code]) - 1):
                sentences[short_lang_code][i].duration = timings[i+1] - timings[i]

        keys = list(sentences.keys())
        for i, v in enumerate(zip(*sentences.values())):
            max_duration = max(x.duration for x in v)
            rs = [max_duration - x.duration for x in v]
            for l, r in zip(keys, rs):
                sentences[l][i].adjustment = r

        for k in keys:
            i = 0
            for line in lines[k]:
                if line.type == 'sentence':
                    line.adjustment = sentences[k][i].adjustment
                    i+=1

        return lines

    def synth_mp3_srt(self, lines: List[ScriptLine], mp3_file_path, srt_file_path, short_lang_code):
        ssml = lines2ssml(lines)
        with open(mp3_file_path, 'wb') as mp3_out, open(srt_file_path, 'w', encoding='utf-8') as srt_out:
            srt_out.write(codecs.BOM_UTF8.decode('utf-8'))
            self._synthesizers[short_lang_code].synthesize(text=ssml, mp3_out=mp3_out, srt_out=srt_out, ssml_input=True)

    def synthesize_all_langs(self, translations: Dict[str, str],
                             mp3_file_paths: Dict[str, str], srt_file_paths: Dict[str, str]):
        adjusted = self._calc_adjustments(translations)
        for short_lang_code, lines in adjusted.items():
            self.synth_mp3_srt(lines, mp3_file_paths[short_lang_code], srt_file_paths[short_lang_code], short_lang_code)