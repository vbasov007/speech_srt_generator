from websynth import turbo
from .element_updates import *


def page_update_on_reset(supported_langs: list, voices: dict):
    return turbo.stream([
        update_textarea(text=""),
        update_select_orig_lang(supported_langs=supported_langs, orig_lang="EN", disabled_orig_lang_change=False),
        update_set_orig_lang(orig_lang="EN"),
        update_makeit(making_error="", download_file_name=""),
        update_select_voices(present_langs=["EN", ], voices=voices),
    ])


def page_update_on_change_orig_lang(orig_lang: str, supported_langs: list, voices: dict):
    return turbo.stream([
        update_set_orig_lang(orig_lang=orig_lang),
        update_select_orig_lang(supported_langs=supported_langs, orig_lang=orig_lang, disabled_orig_lang_change=False),
        update_makeit(making_error="", download_file_name=""),
        update_select_voices(present_langs=[orig_lang, ], voices=voices),
        update_add_translation(supported_langs=supported_langs, present_langs=[orig_lang, ], message="")
    ])


def page_update_on_add_translation_reject(supported_langs: list, present_langs: list, message: str):
    return turbo.stream([
        update_add_translation(supported_langs=supported_langs,
                               present_langs=present_langs,
                               message=message,
                               )
    ])


def page_update_on_add_translation_success(text: str, supported_langs: list, orig_lang: str, present_langs: list,
                                           voices: dict):
    return turbo.stream([
        update_select_orig_lang(supported_langs=supported_langs, orig_lang=orig_lang, disabled_orig_lang_change=True),
        update_add_translation(supported_langs=supported_langs, present_langs=present_langs, message=""),
        update_textarea(text=text),
        update_select_voices(present_langs=present_langs,
                             voices=voices)
    ])

def page_update_makeit(download_file_name="", download_as_name="", error=""):
    return turbo.stream([
        update_makeit(making_error=error, download_file_name=download_file_name, download_as_name=download_as_name)
    ])
