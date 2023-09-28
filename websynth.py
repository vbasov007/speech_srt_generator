import datetime
import hashlib
import os
import threading
import uuid

from flask import Flask, render_template, request, jsonify
from flask import send_from_directory
from turbo_flask import Turbo

import utils
from env import environ
from mp3_srt_synth import Mp3SrtSynth
from multilang import split_translations, add_translation, present_translations

app = Flask(__name__)
turbo = Turbo(app)

from turbo_webpage_elements import *


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

    temp_static_folder = 'static/temp'
    if not os.path.exists(temp_static_folder):
        os.makedirs(temp_static_folder)

    uid = uuid.uuid4()
    temp_zip = os.path.join(folder, f'{uid}.zip')
    voices = Mp3SrtSynth.voices
    supported_langs = Mp3SrtSynth.lang_code_to_name

    if request.method == 'POST':

        if request.form.get('reset'):
            return page_update_on_reset(supported_langs=supported_langs, voices=voices)

        orig_lang = request.form.get("orig_lang")

        if request.form.get('change_orig_lang'):
            orig_lang = request.form.get("selected_orig_lang")
            return page_update_on_change_orig_lang(orig_lang=orig_lang, supported_langs=supported_langs, voices=voices)

        text = request.form['textarea']

        if request.form.get('add_lang'):
            prev_langs = list(set([orig_lang, ] + present_translations(text)))
            new_lang = request.form.get("added_lang")
            if (new_lang in prev_langs) or (new_lang == orig_lang):
                return page_update_on_add_translation_reject(supported_langs=supported_langs,
                                                             present_langs=prev_langs,
                                                             message=f'Language {new_lang} already present'
                                                                     f' or is the original language')

            text = add_translation(text, new_lang, orig_lang,
                                   url=environ.get('translator_url'),
                                   key=environ.get('translator_key'),
                                   verify_cert=not bool(environ.get('ignore_translator_ssl_cert', False)))

            present_langs = list(set([orig_lang, ] + present_translations(text)))

            return page_update_on_add_translation_success(text=text, supported_langs=supported_langs,
                                                          orig_lang=orig_lang, present_langs=present_langs,
                                                          voices=voices)
        if request.form.get("play_current_line"):
            try:
                pos = int(request.form.get("cursor_position"))
            except ValueError:
                return turbo.stream([])

            line_of_text = utils.get_line_by_pos(text, pos)
            translations = split_translations(line_of_text, orig_lang,
                                              present_translations(line_of_text),
                                              ignore_codes=True)

            if len(translations.values()) < 1:
                return page_update_on_text_error("No pronounceable content in the selected line.")

            text_to_play = list(translations.values())[0]
            if len(text_to_play.strip()) < 1:
                return page_update_on_text_error("No pronounceable content in the selected line.")
            lang = list(translations.keys())[0]

            voice = request.form.get(f"voice_{lang}")

            # unique file name for string plus voice id
            fn = hashlib.sha256((text_to_play + voice).encode()).hexdigest()
            temp_file_path = os.path.join(temp_static_folder, f'{fn}.mp3')

            if not os.path.exists(temp_file_path):

                engine = 'standard'
                if voice in Mp3SrtSynth.neural_voices:
                    engine = 'neural'
                converter = Mp3SrtSynth(access_key_id=environ.get('polly_key_id'),
                                        secret_access_key=environ.get('polly_secret_key'),
                                        region=environ.get('polly_region'),
                                        )
                converter.add_lang(voice_id=voice, short_lang_code=lang, engine=engine)
                try:
                    converter.synth_mp3(text=text_to_play, mp3_file_path=temp_file_path, short_lang_code=lang)
                except Exception as e:
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                    if "ssml" in str(e).lower():
                        return page_update_on_text_error(error=f'It appears that there is an error'
                                                               f'in the SSML syntax within the "{text_to_play}"')
                    else:
                        return page_update_on_text_error(error=f'Error: {str(e)}')

            threading.Thread(target=utils.remove_files_after_completion, args=([temp_file_path, ],)).start()

            return page_update_line_player(file_name_mp3=os.path.basename(temp_file_path))

        if request.form.get("makeit"):

            translations = split_translations(text, orig_lang, present_translations(text))

            converter = Mp3SrtSynth(access_key_id=environ.get('polly_key_id'),
                                    secret_access_key=environ.get('polly_secret_key'),
                                    region=environ.get('polly_region'),
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
                if "ssml" in str(e).lower():
                    return page_update_makeit(error='It seems that there might be a mistake'
                                                    ' in the SSML syntax within your input. '
                                                    'To pinpoint the error line, you could try playing each'
                                                    ' line individually using the "Play current line" button.')
                else:
                    return page_update_makeit(error=f'Error: {e}')

            temp_files = list(temp_mp3_paths.values()) + list(temp_srt_paths.values()) + [temp_text_path, ]
            zipped_files = list(zipped_mp3_file_names.values()) + list(zipped_srt_file_names.values()) + [
                zipped_text_file_name, ]

            utils.create_zip_file(temp_zip, temp_files, zipped_files)

            # Return the file for download
            formatted_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            threading.Thread(target=utils.remove_files_after_completion, args=(temp_files + [temp_zip],)).start()

            return page_update_makeit(download_file_name=os.path.basename(temp_zip),
                                      download_as_name=f'mp3_srt_{formatted_datetime}.zip')

    return render_template('index.html', text=None, present_langs=["EN"], orig_lang="EN", voices=voices,
                           supported_langs=supported_langs, error=None, file_name_mp3=None)


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
    # uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    uploads = os.path.join(app.root_path, "output")
    return send_from_directory(uploads, filename, as_attachment=True,
                               download_name=request.args.get("name", "result.zip"))


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


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
    # serve(app, host='0.0.0.0', port=8080)
