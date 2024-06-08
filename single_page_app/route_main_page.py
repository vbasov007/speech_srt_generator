from flask import request, session

from app import app, turbo, worker
from .app_page_controller import AppPageController
from .auth import user_clients, get_authorized_data


@app.route('/', methods=['GET', 'POST'])
def main_page():

    user_id = None
    if session.get("user"):
        kinde_client = user_clients.get(session.get("user"))
        if kinde_client:
            if kinde_client.is_authenticated():
                user_id = get_authorized_data(kinde_client)['user_email']

    page = AppPageController(turbo, request, worker, user_id)

    if request.method == "GET":
        return page.full_render()

    page.restore_context()
    page.text = page.get_textarea()
    page.freeze()

    page.event_loop()

    return page.update()
