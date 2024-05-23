from flask import request

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

    page.event_loop()

    return page.update()
