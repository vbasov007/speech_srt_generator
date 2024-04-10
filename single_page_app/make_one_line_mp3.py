import hashlib
import os

from multilang import split_translations, present_translations


def make_one_line_mp3(line_of_text, voices, orig_lang, converter, temp_folder):
    res = {}

    translations = split_translations(line_of_text, orig_lang,
                                      present_translations(line_of_text),
                                      ignore_codes=True)

    if len(translations.values()) < 1:
        res['error'] = "Put cursor to the line that you want to play!"
        return res

    text_to_play = f'<s>{list(translations.values())[0]}</s>'

    lang = list(translations.keys())[0]

    voice = voices[lang]

    # unique file name for string plus voice id
    fn = hashlib.sha256((text_to_play + voice).encode()).hexdigest()
    temp_file_path = os.path.join(temp_folder, f'{fn}.mp3')

    if not os.path.exists(temp_file_path):
        converter.add_lang(voice_id=voice, short_lang_code=lang)
        try:
            converter.synth_one_phrase_mp3_to_file(text=text_to_play, mp3_file_path=temp_file_path,
                                                   short_lang_code=lang)
        except Exception as e:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            if "ssml" in str(e).lower():
                res['error'] = f'It appears that there is an error'
                f'in the SSML syntax within the "{text_to_play}"'
            else:
                res['error'] = f'Error: {str(e)}'

            return res

    res['file_name_mp3'] = os.path.basename(temp_file_path)

    return res
