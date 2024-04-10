import os
import uuid

import utils
from multilang import split_translations, present_translations


def make_mp3_srt_files(text, voices, orig_lang, present_langs, converter, folder, report_progress=None):
    uid = uuid.uuid4()
    res = {}

    temp_zip = os.path.join(folder, f'{uid}.zip')
    translations = split_translations(text, orig_lang, present_translations(text))

    temp_mp3_paths = {}
    temp_srt_paths = {}
    zipped_mp3_file_names = {}
    zipped_srt_file_names = {}

    temp_text_path = os.path.join(folder, f'{uid}.txt')

    if report_progress:
        report_progress(1.0, "Starting...")

    with open(temp_text_path, "w", encoding="utf-8") as f:
        f.write(utils.unescape_xml_chars(text))

    zipped_text_file_name = r"script.txt"
    for i, lang in enumerate(present_langs):
        converter.add_lang(voice_id=voices[lang], short_lang_code=lang)
        temp_mp3_paths[lang] = os.path.join(folder, f'{uid}_{lang}.mp3')
        temp_srt_paths[lang] = os.path.join(folder, f'{uid}_{lang}.srt')

        if report_progress:
            report_progress(100*i/len(present_langs), "Voice synthesizers initialization")

    try:
        converter.synthesize_all_langs(translations, temp_mp3_paths, temp_srt_paths, report_progress=report_progress)
    except Exception as e:
        if "ssml" in str(e).lower():
            res['error'] = 'It seems that there might be a mistake'
            ' in the SSML syntax within your input. '
            'To pinpoint the error line, you could try playing each'
            ' line individually using the "Play current line" button.'
        else:
            res['error'] = f'Error: {e}'
        return res

    if report_progress:
        report_progress(95.0, "Making result file")

    for lang in present_langs:
        zipped_mp3_file_names[lang] = f'{lang}.mp3'
        zipped_srt_file_names[lang] = f'{lang}.srt'

    temp_files = list(temp_mp3_paths.values()) + list(temp_srt_paths.values()) + [temp_text_path, ]
    zipped_files = list(zipped_mp3_file_names.values()) + list(zipped_srt_file_names.values()) + [
        zipped_text_file_name, ]
    utils.create_zip_file(temp_zip, temp_files, zipped_files)

    res['download_file_name'] = os.path.basename(temp_zip)
    return res
