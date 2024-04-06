from env import environ
from multilang import add_translation, present_translations

def make_translation(text, new_lang, orig_lang):
    res = {}

    try:
        res['text'] = add_translation(text, new_lang, orig_lang,
                               url=environ.get('translator_url'),
                               key=environ.get('translator_key'),
                               verify_cert=not bool(environ.get('ignore_translator_ssl_cert', False)))
    except Exception as e:
        res['error'] = str(e)

    return res
