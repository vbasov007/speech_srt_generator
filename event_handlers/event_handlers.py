from typing import TYPE_CHECKING

import utils
from hotwire_pages import hotwire_event_handler

if TYPE_CHECKING:
    from single_page_app.app_page_controller import AppPageController


@hotwire_event_handler("reset")
def reset_handler(self: 'AppPageController'):
    self.reset()


@hotwire_event_handler("change_orig_lang")
def change_orig_lang_handler(self: 'AppPageController'):
    self.clear_download_link()
    self.orig_lang = self.get_selected_orig_lang()


@hotwire_event_handler("add_lang")
def add_lang_handler(self: 'AppPageController'):
    self.clear_download_link()
    self.add_lang(self.get_added_lang())


@hotwire_event_handler("play_current_line")
def play_current_line_handler(self: 'AppPageController'):
    try:
        pos = self.get_cursor_position()
    except ValueError:
        return
    line_of_text = utils.escape_xml_reserved_chars(utils.get_line_by_pos(self.text, pos))
    self.play_current_line(line_of_text, self.get_voices())


@hotwire_event_handler("makeit")
def makeit_handler(self: 'AppPageController'):
    self.clear_download_link()
    text = utils.escape_xml_reserved_chars(self.text)
    self.makeit_start(text, self.get_voices())


@hotwire_event_handler("refresh_makeit_status")
def refresh_makeit_status_handler(self: 'AppPageController'):
    if self.cur_makeit_worker:
        self.makeit_result()
    if self.cur_translate_worker:
        self.add_lang_result()


@hotwire_event_handler("terminate")
def terminate_handler(self: 'AppPageController'):
    if self.cur_makeit_worker:
        self._worker.clear(self.cur_makeit_worker)
        self.cur_makeit_worker = ""
        self.cur_makeit_progress = 0


@hotwire_event_handler("terminate_translate")
def terminate_translate_handler(self: 'AppPageController'):
    if self.cur_translate_worker:
        self._worker.clear(self.cur_translate_worker)
        self.cur_translate_worker = ""
        self.cur_translate_progress = 0
