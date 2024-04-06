# from flask import Flask
# from turbo_flask import Turbo
# from my_worker import MyWorker
#
# app = Flask(__name__)
# turbo = Turbo(app)
#
# worker = MyWorker(storage={})

from .route_main_page import *
from .route_status import status
from .route_download import download
from .route_help import show_help
