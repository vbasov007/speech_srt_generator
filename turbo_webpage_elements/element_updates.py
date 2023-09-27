from .generic_update import generic_update


def update_textarea(text):
    return generic_update("_textarea.html", "textarea_frame", render=True, text=text)


def update_select_orig_lang(supported_langs: list, orig_lang: str, disabled_orig_lang_change):
    return generic_update("_select_orig_lang.html", "select_orig_lang_frame", render=True,
                          supported_langs=supported_langs,
                          orig_lang=orig_lang,
                          disabled_orig_lang_change=disabled_orig_lang_change
                          )


def update_set_orig_lang(orig_lang):
    return generic_update("_set_orig_lang.html", "set_orig_lang_frame", render=True, orig_lang=orig_lang)


def update_makeit(making_error="", download_file_name="", download_as_name=""):
    return generic_update("_makeit.html", "makeit_frame",
                          render=True,
                          making_error=making_error,
                          download_file_name=download_file_name,
                          download_as_name=download_as_name)


def update_select_voices(present_langs: list, voices):
    return generic_update("_select_voices.html", "select_voices",
                          present_langs=present_langs,
                          voices=voices)


def update_add_translation(supported_langs, present_langs, message):
    return generic_update("_add_translation.html", "add_translation_frame",
                          supported_langs=supported_langs,
                          present_langs=present_langs,
                          translation_message=message
                          )
