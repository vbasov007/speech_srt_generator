import datetime
import os
from typing import List

import html_template_elements
import event_handlers
import utils
from hotwire_pages import HotwirePage, hotwire_event_handler
from mp3_srt_synth import Mp3SrtSynth
from multilang import present_translations
from .constants import TMP_PLAY_FOLDER, RESULT_DOWNLOAD_FOLDER
from .get_converter import get_converter
from .make_one_line_mp3 import make_one_line_mp3
from .make_translation import make_translation
from .maker import make_mp3_srt_files


@utils.extend_with(html_template_elements, event_handlers)
class AppPageController(HotwirePage):

    def __init__(self, turbo_obj, request_obj, worker_obj):
        super().__init__(turbo_obj, request_obj)
        self._worker = worker_obj
        self.main_template = "index.html"

        self.text: str = ""
        self.text_error: str = ""
        self.making_error: str = ""
        self.download_file_name: str = ""
        self.download_as_name: str = ""
        self.message: str = ""
        self.file_name_mp3: str = ""
        self.orig_lang: str = "EN"

        self.supported_langs = Mp3SrtSynth.lang_code_to_name

        # self.add_to_stored_context("orig_lang")

        self.enable_orig_lang_change: bool = True
        # self.add_to_stored_context("enable_orig_lang_change")

        self.cur_makeit_worker: str = ""
        # self.add_to_stored_context("cur_makeit_worker")

        self.cur_translate_worker: str = ""
        # self.add_to_stored_context("cur_translate_worker")

        self.cur_makeit_progress: float = 0
        self.cur_translate_progress: float = 0

        self.voices: list = Mp3SrtSynth.voices

        self._folder = RESULT_DOWNLOAD_FOLDER
        if not os.path.exists(self._folder):
            os.makedirs(self._folder)

        self._temp_static_folder = TMP_PLAY_FOLDER
        if not os.path.exists(self._temp_static_folder):
            os.makedirs(self._temp_static_folder)

        self.add_to_stored_context(["text",
                                    "text_error",
                                    "making_error",
                                    "download_file_name",
                                    "download_as_name",
                                    "orig_lang",
                                    "enable_orig_lang_change",
                                    "cur_makeit_worker",
                                    "cur_translate_worker"
                                    ])

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
        self.cur_makeit_worker: str = ""
        self.cur_makeit_progress: float = 0

    def clear_download_link(self):
        self.download_as_name = ""
        self.download_file_name = ""

    def add_lang(self, new_lang):
        if (new_lang in self.present_langs()) or (new_lang == self.orig_lang):
            self.message = f'Language {new_lang} already present or is the original language'
            return
        self.cur_translate_worker = self._worker.run(make_translation, self.text, new_lang, self.orig_lang)
        return

    def add_lang_result(self):
        status = self._worker.get_status(self.cur_translate_worker)
        if status == 'completed':
            result = self._worker.get_result(self.cur_translate_worker)
            if 'error' in result:
                self.text_error = result['error']
                return

            self.text = utils.unescape_xml_chars(result['text'])
            self.enable_orig_lang_change = False
            self._worker.clear(self.cur_translate_worker)
            self.cur_translate_worker = ""
            self.cur_makeit_progress = 0
            return

        self.cur_translate_progress = self._worker.get_progress(self.cur_translate_worker)

    def play_current_line(self, line_of_text, voices):

        res = make_one_line_mp3(line_of_text, voices, self.orig_lang, get_converter(), self._temp_static_folder)
        if 'error' in res:
            self.text_error = res['error']
            return

        if 'file_name_mp3' in res:
            self.file_name_mp3 = res['file_name_mp3']

        return

    def makeit_start(self, text, voices):
        self.cur_makeit_worker = self._worker.run(make_mp3_srt_files,
                                                  text,
                                                  voices,
                                                  self.orig_lang,
                                                  self.present_langs(),
                                                  get_converter(),
                                                  self._folder
                                                  )

    def makeit_result(self):
        status = self._worker.get_status(self.cur_makeit_worker)
        if status == 'completed':
            result = self._worker.get_result(self.cur_makeit_worker)

            if 'error' in result:
                self.making_error = result['error']
                return

            if "download_file_name" in result:
                self.download_file_name = result['download_file_name']
                formatted_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                self.download_as_name = f'mp3_srt_{formatted_datetime}.zip'

            self._worker.clear(self.cur_makeit_worker)
            self.cur_makeit_worker = ""
            self.cur_makeit_progress = 0

            return

        self.cur_makeit_progress = self._worker.get_progress(self.cur_makeit_worker)

    def present_langs(self) -> List[str]:
        return list(set([self.orig_lang, ] + present_translations(self.text)))

    def get_textarea(self):
        return self.get_request_form_value("textarea")

    def get_selected_orig_lang(self):
        return self.get_request_form_value("selected_orig_lang")

    def get_voices(self):
        return {lang: self.get_request_form_value(f"voice_{lang}") for lang in self.present_langs()}

    def get_added_lang(self):
        return self.get_request_form_value("added_lang")

    def get_cursor_position(self):
        return int(self.get_request_form_value("cursor_position"))
