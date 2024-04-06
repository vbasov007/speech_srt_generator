from flask import send_from_directory

from app import app


@app.route('/help')
def show_help():
    return send_from_directory('../templates', 'help.html')
