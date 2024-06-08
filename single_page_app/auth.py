import os
from datetime import date
from functools import wraps

from flask import url_for, session, request
from kinde_sdk import Configuration
from kinde_sdk.kinde_api_client import GrantType, KindeApiClient

from app import app

configuration = Configuration(host=os.getenv("kinde_host"))
kinde_api_client_params = {
    "configuration": configuration,
    "domain": os.getenv("kinde_host"),
    "client_id": os.getenv("kinde_client_id"),
    "client_secret": os.getenv("kinde_client_secret"),
    "grant_type": GrantType.AUTHORIZATION_CODE,
    "callback_url": os.getenv("kinde_callback_url")
}

kinde_client = KindeApiClient(**kinde_api_client_params)
from authlib.common.security import generate_token

CODE_VERIFIER = generate_token(48)
kinde_api_client_params["code_verifier"] = CODE_VERIFIER

user_clients = {}


def get_authorized_data(kinde_cl):
    user = kinde_cl.get_user_details()
    return {
        "id": user.get("id"),
        "user_given_name": user.get("given_name"),
        "user_family_name": user.get("family_name"),
        "user_email": user.get("email"),
        "user_picture": user.get("picture"),
    }


def login_required(user):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not user.is_authenticated():
                return app.redirect(url_for('index'))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


@app.route("/api/auth/login")
def login():
    return app.redirect(kinde_client.get_login_url())


@app.route("/api/auth/register")
def register():
    return app.redirect(kinde_client.get_register_url())


# @app.route("/api/auth/kinde_callback")
@app.route("/callback")
def callback():
    kinde_client.fetch_token(authorization_response=request.url)
    data = {"current_year": date.today().year}
    data.update(get_authorized_data(kinde_client))
    session["user"] = data.get("id")
    user_clients[data.get("id")] = kinde_client
    return app.redirect(url_for("main_page"))


@app.route("/api/auth/logout")
def logout():
    user_clients[session.get("user")] = None
    session["user"] = None
    return app.redirect(
        kinde_client.logout(redirect_to=url_for("main_page"))
    )

# @app.route("/details")
# def get_details():
#     template = "logged_out.html"
#     if session.get("user"):
#         kinde_client = user_clients.get(session.get("user"))
#         data = {"current_year": date.today().year}
#         data.update(get_authorized_data(kinde_client))
#         data["access_token"] = kinde_client.configuration.access_token
#         template = "details.html"
#     return render_template(template, **data)
