import datetime
import os
import threading
import time
import uuid
import zipfile
from multilang import split_translations, add_translation, present_translations

from flask import Flask, render_template, request, send_file

from synth import converter

app = Flask(__name__)

args = {'--config': 'config.yaml',
        '--input': 'input.txt',
        '--mp3': 'res.mp3',
        '--out_folder': 'output',
        '--srt': 'res.srt'}


def create_zip_file(zip_file_path, file_paths: list, zipped_file_names: list = None):
    with zipfile.ZipFile(zip_file_path, 'w') as zip_file:

        if zipped_file_names is None:
            zipped_file_names = [os.path.basename(file_path) for file_path in file_paths]

        for file_path, zipped_name in zip(file_paths, zipped_file_names):
            zip_file.write(file_path, zipped_name)


def remove_files_after_completion(file_paths: list, delay: int = 5, repeat: int = 10):
    not_deleted = file_paths.copy()
    for i in range(repeat):
        if len(not_deleted) == 0:
            break
        time.sleep(delay)
        remaining = not_deleted.copy()
        for f in remaining:
            try:
                os.remove(f)
            except:
                pass
            else:
                print(f'Removed {f}')
                not_deleted.remove(f)

from flask import send_from_directory

@app.route('/help')
def show_help():
    return send_from_directory('templates', 'help.html')

@app.route('/', methods=['GET', 'POST'])
def home():
    folder = 'output'
    uid = uuid.uuid4()
    temp_mp3 = os.path.join(folder, f'{uid}.mp3')
    temp_srt = os.path.join(folder, f'{uid}.srt')
    temp_zip = os.path.join(folder, f'{uid}.zip')

    if request.method == 'POST':
        text = request.form['textarea']
        language_code = request.form.get('language')
        voice_id = request.form.get('voice')
        prev_langs = present_translations(text)
        new_lang = request.form.get("added_lang")
        orig_lang = request.form.get("orig_lang")
        if request.form.get('add_lang'):
            if (new_lang in prev_langs) or (new_lang == orig_lang):
                return render_template('index.html', text=text,
                                       present_langs=prev_langs,
                                       error=f'Language {new_lang} already present or is the original language')
            text = add_translation(text, new_lang, orig_lang)
            return render_template('index.html', text=text, present_langs=present_translations(text), error=None)

        text_dict = split_translations(text, orig_lang, present_translations(text))

        try:
            error_log = converter(args, text_dict["DE"], output_folder=folder, mp3_file=f'{uid}.mp3', srt_file=f'{uid}.srt',
                                  voice_id=voice_id, language_code=language_code)
        except Exception:
            import traceback
            return render_template('error.html', error=traceback.format_exc(), lines=[])

        if error_log:
            return render_template('error.html', lines=error_log, error=None)

        create_zip_file(temp_zip, [temp_mp3, temp_srt], ['res.mp3', 'res.srt'])

        # Return the file for download
        formatted_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        threading.Thread(target=remove_files_after_completion, args=([temp_mp3, temp_srt, temp_zip],)).start()

        return send_file(temp_zip, as_attachment=True, download_name=f'mp3_srt_{formatted_datetime}.zip')

    return render_template('index.html', text=None, present_langs=[], error=None)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
