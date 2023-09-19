import datetime
import os
import threading
import time
import uuid
import zipfile

from flask import Flask, render_template, request, send_file, jsonify
from waitress import serve

from mp3_srt_synth import Mp3SrtSynth
from multilang import split_translations, add_translation, present_translations

from mylogger import mylog

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
                mylog.error(f'Failed to remove {f}')
            else:
                mylog.info(f'Removed {f}')
                not_deleted.remove(f)


from flask import send_from_directory


@app.route('/help')
def show_help():
    return send_from_directory('templates', 'help.html')


@app.route('/', methods=['GET', 'POST'])
def home():
    folder = 'output'
    # if folder does not exist, create it
    if not os.path.exists(folder):
        os.makedirs(folder)

    uid = uuid.uuid4()
    temp_zip = os.path.join(folder, f'{uid}.zip')
    voices = Mp3SrtSynth.voices
    supported_langs = Mp3SrtSynth.lang_code_to_name
    if request.method == 'POST':
        if request.form.get('reset'):
            return render_template('index.html', text='',
                                   present_langs=['EN', ],
                                   orig_lang="EN",
                                   voices=voices,
                                   supported_langs=supported_langs,
                                   error=None)

        text = request.form['textarea']
        orig_lang = request.form.get("orig_lang")
        prev_langs = list(set([orig_lang, ] + present_translations(text)))
        new_lang = request.form.get("added_lang")
        if request.form.get('add_lang'):
            if (new_lang in prev_langs) or (new_lang == orig_lang):
                return render_template('index.html', text=text,
                                       present_langs=prev_langs,
                                       orig_lang=orig_lang,
                                       supported_langs=supported_langs,
                                       voices=voices,
                                       error=f'Language {new_lang} already present or is the original language')
            text = add_translation(text, new_lang, orig_lang,
                                   verify_cert=not bool(os.environ.get('ignore_translator_ssl_cert', False)))
            present_langs = list(set([orig_lang, ] + present_translations(text)))
            return render_template('index.html', text=text,
                                   present_langs=present_langs,
                                   orig_lang=orig_lang,
                                   voices=voices,
                                   supported_langs=supported_langs,
                                   error=None)

        translations = split_translations(text, orig_lang, present_translations(text))

        converter = Mp3SrtSynth(access_key_id=os.environ.get('polly_key_id'),
                                secret_access_key=os.environ.get('polly_secret_key'),
                                region=os.environ.get('polly_region'),
                                )

        temp_mp3_paths = {}
        temp_srt_paths = {}
        zipped_mp3_file_names = {}
        zipped_srt_file_names = {}

        present_langs = list(set([orig_lang, ] + present_translations(text)))
        for lang in present_langs:
            voice = request.form.get(f"voice_{lang}")
            engine = 'standard'
            if voice in Mp3SrtSynth.neural_voices:
                engine = 'neural'
            converter.add_lang(voice_id=request.form.get(f"voice_{lang}"), short_lang_code=lang, engine=engine)
            temp_mp3_paths[lang] = os.path.join(folder, f'{uid}_{lang}.mp3')
            temp_srt_paths[lang] = os.path.join(folder, f'{uid}_{lang}.srt')
            zipped_mp3_file_names[lang] = f'{lang}.mp3'
            zipped_srt_file_names[lang] = f'{lang}.srt'

        try:
            converter.synthesize_all_langs(translations, temp_mp3_paths, temp_srt_paths)
        except Exception as e:
            return render_template('index.html', text=text,
                                   present_langs=present_langs,
                                   orig_lang=orig_lang,
                                   voices=voices,
                                   supported_langs=supported_langs,
                                   error=f'Error: {e}')

        temp_files = list(temp_mp3_paths.values()) + list(temp_srt_paths.values())
        zipped_files = list(zipped_mp3_file_names.values()) + list(zipped_srt_file_names.values())

        create_zip_file(temp_zip, temp_files, zipped_files)

        # Return the file for download
        formatted_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        threading.Thread(target=remove_files_after_completion, args=(temp_files + [temp_zip],)).start()

        return send_file(temp_zip, as_attachment=True, download_name=f'mp3_srt_{formatted_datetime}.zip')

    return render_template('index.html', text=None, present_langs=["EN"], orig_lang="EN", voices=voices,
                           supported_langs=supported_langs, error=None)


@app.route('/change_orig_lang', methods=['GET', 'POST'])
def change_orig_lang():
    voices = Mp3SrtSynth.voices
    supported_langs = Mp3SrtSynth.lang_code_to_name
    selected_lang = request.form.get('selectedValue')
    return jsonify({"content": render_template('index.html', text="",
                                               present_langs=[selected_lang, ],
                                               orig_lang=selected_lang,
                                               voices=voices,
                                               supported_langs=supported_langs, error=None)})


if __name__ == '__main__':
    # app.run(debug=False, host='0.0.0.0', port=8080)
    serve(app, host='0.0.0.0', port=8080)