import os
from env import environ
from flask import request, render_template

from app import app
from test_external_services import test_polly, test_translator, check_folder_access


@app.route('/status', methods=['GET', 'POST'])
def status():
    hide_secrets = environ.copy()
    secret_key = hide_secrets['polly_secret_key']
    hide_secrets['polly_secret_key'] = secret_key[:4] + '*' * (len(secret_key) - 8) + secret_key[-4:]
    secret_key = hide_secrets['translator_key']
    hide_secrets['translator_key'] = secret_key[:4] + '*' * (len(secret_key) - 8) + secret_key[-4:]
    secret_key = hide_secrets['polly_key_id']
    hide_secrets['polly_key_id'] = secret_key[:4] + '*' * (len(secret_key) - 8) + secret_key[-4:]

    hide_secrets["abspath for temp_file_folder"] = os.path.abspath(hide_secrets['temp_file_folder'])
    hide_secrets["Access to temp_file_folder"] = check_folder_access(hide_secrets["abspath for temp_file_folder"])
    hide_secrets["abspath for temp_play_folder"] = os.path.abspath(hide_secrets['temp_play_folder'])
    hide_secrets["Access to temp_play_folder"] = check_folder_access(hide_secrets["abspath for temp_play_folder"])

    if request.method == 'POST':
        if request.form.get("test_polly"):
            test_result = test_polly()
            return render_template("status.html", environ=hide_secrets, aws_polly_test_result=test_result,
                                   translator_test_result="")
        if request.form.get('test_translator'):
            test_result = test_translator()
            return render_template("status.html", environ=hide_secrets, aws_polly_test_result="",
                                   translator_test_result=test_result)
    return render_template("status.html", environ=hide_secrets, aws_polly_test_result="", translator_test_result="")
