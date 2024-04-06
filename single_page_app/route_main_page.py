from flask import request

import utils
from app import app, turbo
from .app_page_controller import AppPageController


@app.route('/', methods=['GET', 'POST'])
def main_page():
    page = AppPageController(turbo)

    if request.method == "GET":
        return page.full_render()

    page.restore_context(request)

    page.text = request.form['textarea']

    voices = {l: request.form.get(f"voice_{l}") for l in page.present_langs()}

    if request.form.get('reset'):
        page.reset()
    elif request.form.get('change_orig_lang'):
        page.orig_lang = request.form.get("selected_orig_lang")

    elif request.form.get('add_lang'):
        new_lang = request.form.get("added_lang")
        page.add_lang(new_lang)

    elif request.form.get("play_current_line"):
        try:
            pos = int(request.form.get("cursor_position"))
        except ValueError:
            return page.update()
        line_of_text = utils.escape_xml_reserved_chars(utils.get_line_by_pos(page.text, pos))
        page.play_current_line(line_of_text, voices)

    elif request.form.get("makeit"):
        text = utils.escape_xml_reserved_chars(page.text)
        page.makeit(text, voices)

    return page.update()


