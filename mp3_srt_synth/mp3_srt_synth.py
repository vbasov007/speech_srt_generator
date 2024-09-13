import codecs
from typing import List, Dict, Callable, Optional

from aws_speech_synthesizer import AwsSpeechSynthesizer
from utils.text2lines import text2lines, lines2ssml, ScriptLine


class Mp3SrtSynthException(Exception):
    pass


class Mp3SrtSynth:
    long_lang_code = {
        'EN': 'en-US',
        'DE': 'de-DE',
        'FR': 'fr-FR',
        'ES': 'es-ES',
        'IT': 'it-IT',
        'PL': 'pl-PL',
        'PT': 'pt-PT',
        'RU': 'ru-RU',
        'JA': 'ja-JP',
        'ZH': 'cmn-CN',
        'AR': 'ar-AE',
        'NL': 'nl-NL',
        'CS': 'cs-CZ',
        'DA': 'da-DK',
        'FI': 'fi-FI',
        'KO': 'ko-KR',
        'NB': 'nb-NO',
        'SV': 'sv-SE',
        'TR': 'tr-TR'
    }

    lang_code_to_name = {
        'EN': 'English',
        'DE': 'Deutsch',
        'FR': 'Français',
        'ES': 'Español',
        'IT': 'Italiano',
        'PL': 'Polski',
        'PT': 'Português',
        'RU': 'Русский',
        'JA': 'Japanese',
        'ZH': 'Chinese',
        'AR': 'Arabic (Gulf)',
        'NL': 'Dutch',
        'CS': 'Czech',
        'DA': 'Danish',
        'FI': 'Finnish',
        'KO': 'Korean',
        'NB': 'Norwegian',
        'SV': 'Swedish',
        'TR': 'Turkish'

    }

    voices = {
        "EN": ['Danielle', 'Gregory', 'Ivy', 'Joanna*', 'Kendra', 'Kimberly', 'Salli', 'Joey', 'Justin', 'Kevin',
               'Matthew', 'Ruth', 'Stephen'],
        "DE": ["Daniel", "Vicki"],
        "FR": ["Lea", "Remi"],
        "IT": ["Bianca", "Adriano"],
        "ZH": ["Zhiyu", ],
        "JA": ["Kazuha", "Takumi", "Tomoko"],
        "RU": ["Maxim", "Tatyana"],
        'ES': ['Lucia', 'Sergio'],
        'PL': ['Ola'],
        'PT': ['Ines'],
        'AR': ['Hala', 'Zayd'],
        'NL': ['Laura'],
        'CS': ['Jitka'],
        'DA': ['Sofie'],
        'FI': ['Suvi'],
        'KO': ['Seoyeon'],
        'NB': ['Ida'],
        'SV': ['Elin'],
        'TR': ['Burcu']

    }

    neural_voices = ['Danielle', 'Gregory', 'Ivy', 'Joanna*', 'Kendra', 'Kimberly', 'Salli', 'Joey', 'Justin', 'Kevin',
               'Matthew', 'Ruth', 'Stephen',
                "Daniel", "Vicki",
                "Lea", "Remi",
                "Bianca", "Adriano",
                "Zhiyu",
                "Kazuha", "Takumi", "Tomoko",
                'Lucia', 'Sergio', 'Ola',
                'Ines',
                'Hala', 'Zayd',
                'Laura',
                'Jitka',
                'Sofie',
                'Suvi',
                'Seoyeon',
                'Ida',
                'Elin',
                'Burcu']

    def __init__(self, access_key_id, secret_access_key, region):
        self._access_key_id = access_key_id
        self._secret_access_key = secret_access_key
        self._region = region
        self._synthesizers: Dict[str, AwsSpeechSynthesizer] = {}

    def add_lang(self, voice_id, short_lang_code, speech_style="conversational", engine=None):
        if engine is None:
            if voice_id in self.neural_voices:
                engine = 'neural'
            else:
                engine = "standard"

        self._synthesizers[short_lang_code] = AwsSpeechSynthesizer(access_key_id=self._access_key_id,
                                                                   secret_access_key=self._secret_access_key,
                                                                   region_name=self._region,
                                                                   engine=engine,
                                                                   voice_id=voice_id,
                                                                   speech_style=speech_style,
                                                                   language_code=self.long_lang_code[short_lang_code],
                                                                   )

    def _calc_adjustments(self, translations: Dict[str, str]) -> Dict[str, List[ScriptLine]]:
        lines: Dict[str, List[ScriptLine]] = {}
        sentences: Dict[str, List[ScriptLine]] = {}
        for short_lang_code, text in translations.items():

            lines[short_lang_code] = text2lines(text)
            ssml = lines2ssml(lines[short_lang_code])
            timings = self._synthesizers[short_lang_code].start_sentence_timings(ssml)
            sentences[short_lang_code] = [x for x in lines[short_lang_code] if x.type == 'sentence']
            for i in range(len(sentences[short_lang_code]) - 1):
                sentences[short_lang_code][i].time_to_next = timings[i + 1] - timings[i]

        keys = list(sentences.keys())
        for i, v in enumerate(zip(*sentences.values())):
            max_duration = max(x.time_to_next for x in v)
            rs = [max_duration - x.time_to_next for x in v]
            for l, r in zip(keys, rs):
                sentences[l][i].adjustment = r

        for k in keys:
            i = 0
            for line in lines[k]:
                if line.type == 'sentence':
                    line.adjustment = sentences[k][i].adjustment
                    i += 1

        # apply absolute timings
        for k in keys:
            absolut_time = 0
            for line in lines[k]:
                if line.type == 'break':
                    continue
                absolut_time += line.time_to_next + line.adjustment
                if line.type == "time_mark":
                    if line.absolute_start_time > absolut_time:
                        line.adjustment = line.absolute_start_time - absolut_time
                        absolut_time = line.absolute_start_time

        return lines

    def synth_mp3_srt_to_files(self, lines: List[ScriptLine], mp3_file_path, srt_file_path, short_lang_code):
        ssml = lines2ssml(lines)
        with open(mp3_file_path, 'wb') as mp3_out, open(srt_file_path, 'w', encoding='utf-8') as srt_out:
            srt_out.write(codecs.BOM_UTF8.decode('utf-8'))
            self._synthesizers[short_lang_code].synth_speech_and_subtitles_to_files(text=ssml, mp3_out=mp3_out,
                                                                                    srt_out=srt_out, ssml_input=True)

    def synth_one_phrase_mp3_to_file(self, text, mp3_file_path, short_lang_code):
        # ssml = f'<speak>{text}</speak>'
        with open(mp3_file_path, 'wb') as mp3_out:
            self._synthesizers[short_lang_code].synth_speech_and_subtitles_to_files(text=text, mp3_out=mp3_out,
                                                                                    ssml_input=True)

    def synthesize_all_langs(self, translations: Dict[str, str],
                             mp3_file_paths: Dict[str, str], srt_file_paths: Dict[str, str],
                             report_progress: Optional[Callable] = None):

        adjusted = self._calc_adjustments(translations)

        if report_progress:
            report_progress(1.0, "Making voice")

        num_of_lang = len(adjusted)
        count = 0
        for short_lang_code, lines in adjusted.items():
            self.synth_mp3_srt_to_files(lines, mp3_file_paths[short_lang_code],
                                        srt_file_paths[short_lang_code], short_lang_code)
            count += 1

            if report_progress:
                report_progress(100 * count / num_of_lang, f"Making {short_lang_code}")

