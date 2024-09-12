from flask import redirect

from app import app


@app.route('/help')
def show_help():
    return "<h2>Sorry! This part is not ready yet.<br>" \
           "Ask for training the author: Vasily Basov <a href='mailto:vasily.basov@infineon.com'>vasily.basov@infineon.com</a></h2>"

@app.route('/training-video')
def show_training_video():
    return "<h2>Sorry! This part is not ready yet.<br>" \
           "Ask for training the author: Vasily Basov <a href='mailto:vasily.basov@infineon.com'>vasily.basov@infineon.com</a></h2>"
