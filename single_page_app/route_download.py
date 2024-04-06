import os

from flask import send_from_directory, request

from single_page_app.constants import TMP_PLAY_FOLDER, RESULT_DOWNLOAD_FOLDER
from utils import delete_old_files

from app import app


@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    uploads = os.path.join(app.root_path, RESULT_DOWNLOAD_FOLDER)
    delete_old_files(uploads, ext_list=[".mp3", ".txt", ".zip", ".srt"], age_seconds=600)
    return send_from_directory(directory=uploads, path=filename, as_attachment=True,
                               download_name=request.args.get("name", "result.zip"))


@app.route('/play/<filename>', methods=['GET'])
def play_line(filename):
    tmp_play_folder = os.path.join(app.root_path, TMP_PLAY_FOLDER)
    delete_old_files(tmp_play_folder, ext_list=[".mp3",], age_seconds=600)
    return send_from_directory(directory=tmp_play_folder, path=filename, as_attachment=True)
