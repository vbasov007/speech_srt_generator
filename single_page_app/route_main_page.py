from flask import request

import utils
from app import app, turbo, worker
from .app_page_controller import AppPageController


@app.route('/', methods=['GET', 'POST'])
def main_page():
    page = AppPageController(turbo, request, worker)

    if request.method == "GET":
        return page.full_render()

    page.restore_context()
    page.text = page.get_textarea()
    page.freeze()

    voices = page.get_voices()

    if page.is_action_reset():
        page.reset()

    elif page.is_action_change_orig_lang():
        page.orig_lang = page.get_selected_orig_lang()

    elif page.is_action_add_lang():
        page.add_lang(page.get_added_lang())

    elif page.is_action_play_current_line():
        try:
            pos = page.get_cursor_position()
        except ValueError:
            return page.update()
        line_of_text = utils.escape_xml_reserved_chars(utils.get_line_by_pos(page.text, pos))
        page.play_current_line(line_of_text, voices)

    elif page.is_action_makeit():
        text = utils.escape_xml_reserved_chars(page.text)
        # page.makeit(text, voices)
        page.makeit_start(text, voices)

    elif page.is_action_refresh_makeit_progress():
        if page.cur_makeit_worker:
            page.makeit_result()

        if page.cur_translate_worker:
            page.add_lang_result()

    elif page.is_action_terminate():
        if page.cur_makeit_worker:
            worker.clear(page.cur_makeit_worker)
            page.cur_makeit_worker = ""
            page.cur_makeit_progress = 0

    elif page.is_action_terminate_translate():
        if page.cur_translate_worker:
            worker.clear(page.cur_translate_worker)
            page.cur_translate_worker = ""
            page.cur_translate_progress = 0

    return page.update()
