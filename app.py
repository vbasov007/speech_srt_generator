from flask import Flask
from turbo_flask import Turbo
from flask_session import Session
from my_worker import MyWorker

app = Flask(__name__)
turbo = Turbo(app)

app.config.from_object("auth_config")
Session(app)

worker = MyWorker(storage={})

from single_page_app import *


if __name__ == '__main__':
    app.run()