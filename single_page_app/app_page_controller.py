import datetime
import os
from typing import List

import utils
from app import worker
from hotwire_pages import HotwirePage
from mp3_srt_synth import Mp3SrtSynth
from multilang import present_translations
from .constants import TMP_PLAY_FOLDER, RESULT_DOWNLOAD_FOLDER
from .get_converter import get_converter
from .make_one_line_mp3 import make_one_line_mp3
from .make_translation import make_translation
from .maker import make_mp3_srt_files


class AppPageController(HotwirePage):

    def __init__(self, turbo):
        super().__init__(turbo)
        self.main_template = "index.html"

        self.text: str = ""
        self.text_error: str = ""
        self.making_error: str = ""
        self.download_file_name: str = ""
        self.download_as_name: str = ""
        self.message: str = ""
        self.file_name_mp3: str = ""
        self.orig_lang: str = ""

        self.reset()

        self.supported_langs = Mp3SrtSynth.lang_code_to_name

        self.add_to_stored_context("orig_lang")

        self.enable_orig_lang_change: bool = True
        self.add_to_stored_context("enable_orig_lang_change")

        self.voices: list = Mp3SrtSynth.voices

        self._folder = RESULT_DOWNLOAD_FOLDER
        # if folder does not exist, create it
        if not os.path.exists(self._folder):
            os.makedirs(self._folder)

        self._temp_static_folder = TMP_PLAY_FOLDER
        if not os.path.exists(self._temp_static_folder):
            os.makedirs(self._temp_static_folder)

        self.register(self.incl_line_player)
        self.register(self.incl_textarea)
        self.register(self.incl_text_error)
        self.register(self.incl_select_orig_lang)
        self.register(self.incl_makeit)
        self.register(self.incl_select_voices)
        self.register(self.incl_add_translation)

    def reset(self):
        self.text = ""
        self.text_error = ""
        self.making_error = ""
        self.orig_lang = "EN"
        self.download_file_name = ""
        self.download_as_name = ""
        self.message: str = ""
        self.file_name_mp3 = ""
        self.enable_orig_lang_change = True

    def add_lang(self, new_lang):
        if (new_lang in self.present_langs()) or (new_lang == self.orig_lang):
            self.message = f'Language {new_lang} already present or is the original language'
            return

        res = make_translation(self.text, new_lang, self.orig_lang)

        if 'error' in res:
            self.text_error = f"Can't add language: {res['error']}"
            return

        self.text = utils.unescape_xml_chars(res['text'])
        self.enable_orig_lang_change = False
        return

    def play_current_line(self, line_of_text, voices):

        res = make_one_line_mp3(line_of_text, voices, self.orig_lang, get_converter(), self._temp_static_folder)
        if 'error' in res:
            self.text_error = res['error']
            return

        if 'file_name_mp3' in res:
            self.file_name_mp3 = res['file_name_mp3']

        return

    def makeit(self, text, voices):

        res = make_mp3_srt_files(text,
                                 voices,
                                 self.orig_lang,
                                 self.present_langs(),
                                 get_converter(),
                                 self._folder)

        if "error" in res:
            self.making_error = res['error']
            return

        if "download_file_name" in res:
            self.download_file_name = res['download_file_name']
            formatted_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.download_as_name = f'mp3_srt_{formatted_datetime}.zip'

        return

    # def makeit_start(self, text, voices):
    #     worker.run()

    def present_langs(self) -> List[str]:
        return list(set([self.orig_lang, ] + present_translations(self.text)))

    def incl_textarea(self):
        return self.get_html(self.cur_func_name(), template_name="_textarea.html", text=self.text)

    def incl_text_error(self):
        return self.get_html(self.cur_func_name(), template_name="_text_error.html", text=self.text_error)

    def incl_select_orig_lang(self):
        return self.get_html(self.cur_func_name(), template_name="_select_orig_lang.html",
                             supported_langs=self.supported_langs,
                             orig_lang=self.orig_lang,
                             enable_orig_lang_change=self.enable_orig_lang_change)

    def incl_makeit(self):
        return self.get_html(self.cur_func_name(), template_name="_makeit.html",
                             making_error=self.making_error,
                             download_file_name=self.download_file_name,
                             download_as_name=self.download_as_name)

    def incl_select_voices(self):
        return self.get_html(self.cur_func_name(), template_name="_select_voices.html",
                             present_langs=self.present_langs(),
                             voices=self.voices)

    def incl_add_translation(self):
        return self.get_html(self.cur_func_name(), template_name="_add_translation.html",
                             supported_langs=self.supported_langs,
                             present_langs=self.present_langs(),
                             translation_message=self.message)

    def incl_line_player(self):
        return self.get_html(self.cur_func_name(), template_name="_line_player.html",
                             file_name_mp3=self.file_name_mp3)
