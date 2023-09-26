import datetime
import os
import threading
import time
import uuid
import zipfile

from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
from turbo_flask import Turbo
from waitress import serve

from mp3_srt_synth import Mp3SrtSynth
from multilang import split_translations, add_translation, present_translations

from progress_indicator import ProgressIndicator

from mylogger import mylog

app = Flask(__name__)
turbo = Turbo(app)

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


def remove_files_after_completion(file_paths: list, delay: int = 600, repeat: int = 10):
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
    app.config['UPLOAD_FOLDER'] = folder
    # if folder does not exist, create it
    if not os.path.exists(folder):
        os.makedirs(folder)

    uid = uuid.uuid4()
    temp_zip = os.path.join(folder, f'{uid}.zip')
    voices = Mp3SrtSynth.voices
    supported_langs = Mp3SrtSynth.lang_code_to_name
    if request.method == 'POST':
        orig_lang = request.form.get("orig_lang")
        if request.form.get('reset'):
            orig_lang = "EN"
            return turbo.stream([
                turbo.update(render_template("_textarea.html", text=""), target="textarea_frame"),
                turbo.update(render_template("_select_orig_lang.html",
                                             supported_langs=supported_langs,
                                             orig_lang=orig_lang,
                                             disabled_orig_lang_change=False),
                             target="select_orig_lang_frame"),
                turbo.update(render_template("_set_orig_lang.html", orig_lang=orig_lang),
                             target="set_orig_lang_frame"),
                turbo.update(render_template("_makeit.html", making_error="", download_file_path=""),
                             target="makeit_frame"),
                turbo.update(render_template("_select_voices.html",
                                             present_langs=['EN'],
                                             voices=voices),
                             target="select_voices")
            ])

        if request.form.get('change_orig_lang'):
        # if request.form.get("selected_orig_lang") != orig_lang:
            orig_lang = request.form.get("selected_orig_lang")
            return turbo.stream([
                turbo.update(render_template("_set_orig_lang.html", orig_lang=orig_lang),
                             target="set_orig_lang_frame"),
                turbo.update(render_template("_select_orig_lang.html",
                                             supported_langs=supported_langs,
                                             orig_lang=orig_lang,
                                             disabled_orig_lang_change=False),
                             target="select_orig_lang_frame"),
                turbo.update(render_template("_makeit.html", making_error="", download_file_path=""),
                             target="makeit_frame"),
                turbo.update(render_template("_select_voices.html",
                                             present_langs=[orig_lang],
                                             voices=voices),
                             target="select_voices"),
                turbo.update(render_template("_add_translation.html",
                                             supported_langs=supported_langs,
                                             present_langs=[orig_lang],
                                             ), target="add_translation_frame")

            ])


        text = request.form['textarea']
        prev_langs = list(set([orig_lang, ] + present_translations(text)))
        new_lang = request.form.get("added_lang")
        if request.form.get('add_lang'):
            if (new_lang in prev_langs) or (new_lang == orig_lang):
                return turbo.stream([
                    turbo.update(render_template("_add_translation.html",
                                                 supported_langs=supported_langs,
                                                 present_langs=prev_langs,
                                                 translation_message=f'Language {new_lang} already present or is the original language',
                                                 ), target="add_translation_frame")
                ])

            translation_pi = ProgressIndicator("translation-progress-info", app, turbo, "_translation_progress_info.html")
            text = add_translation(text, new_lang, orig_lang,
                                   verify_cert=not bool(os.environ.get('ignore_translator_ssl_cert', False)),
                                   progress_indicator=translation_pi.message)
            translation_pi.clear()

            present_langs = list(set([orig_lang, ] + present_translations(text)))
            return turbo.stream([
                turbo.update(render_template("_select_orig_lang.html",
                                             disabled_orig_lang_change=True,
                                             supported_langs=supported_langs,
                                             orig_lang=orig_lang),
                             target="select_orig_lang_frame"),
                turbo.update(render_template("_add_translation.html",
                                             supported_langs=supported_langs,
                                             present_langs=prev_langs,
                                             ), target="add_translation_frame"),
                turbo.update(render_template("_textarea.html", text=text),
                             target="textarea_frame"),
                turbo.update(render_template("_select_voices.html",
                                             present_langs=present_langs,
                                             voices=voices),
                             target="select_voices")
            ])

        translations = split_translations(text, orig_lang, present_translations(text))

        pi = ProgressIndicator("progress-info", app, turbo, "_synth_progress_info.html")
        converter = Mp3SrtSynth(access_key_id=os.environ.get('polly_key_id'),
                                secret_access_key=os.environ.get('polly_secret_key'),
                                region=os.environ.get('polly_region'),
                                progress=pi.message,
                                )

        temp_mp3_paths = {}
        temp_srt_paths = {}
        zipped_mp3_file_names = {}
        zipped_srt_file_names = {}

        present_langs = list(set([orig_lang, ] + present_translations(text)))
        temp_text_path = os.path.join(folder, f'{uid}.txt')
        with open(temp_text_path, "w", encoding="utf-8") as f:
            f.write(text)
        zipped_text_file_name = r"script.txt"
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
            return turbo.stream([
                turbo.update(render_template("_makeit.html", making_error=f'Error: {e}'), target="makeit_frame")
            ])

        pi.clear()

        temp_files = list(temp_mp3_paths.values()) + list(temp_srt_paths.values()) + [temp_text_path,]
        zipped_files = list(zipped_mp3_file_names.values()) + list(zipped_srt_file_names.values()) + [zipped_text_file_name,]

        create_zip_file(temp_zip, temp_files, zipped_files)

        # Return the file for download
        formatted_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        threading.Thread(target=remove_files_after_completion, args=(temp_files + [temp_zip],)).start()

        return turbo.stream([
            turbo.update(render_template("_makeit.html",
                                         download_file_path=os.path.basename(temp_zip),
                                         download_name=f'mp3_srt_{formatted_datetime}.zip'
                                         ),
                         target="makeit_frame")
        ])

            # redirect(url_for('download', file_path=temp_zip, download_name=f'mp3_srt_{formatted_datetime}.zip'))
        # return send_file(temp_zip, as_attachment=True, download_name=f'mp3_srt_{formatted_datetime}.zip')

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

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(uploads,  filename, as_attachment=True, download_name=request.args.get("name", "result.zip"))
    # return send_file(file_path, as_attachment=True, download_name=download_name)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
    # serve(app, host='0.0.0.0', port=8080)