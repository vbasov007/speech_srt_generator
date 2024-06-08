from typing import TYPE_CHECKING

from hotwire_pages import hotwire_html_template_element

if TYPE_CHECKING:
    from single_page_app.app_page_controller import AppPageController


@hotwire_html_template_element()
def incl_textarea(self: 'AppPageController'):
    return self.get_html(self.cur_func_name(), template_name="_textarea.html", text=self.text,
                         disabled=bool(self.cur_translate_worker) or bool(self.cur_makeit_worker))


@hotwire_html_template_element()
def incl_text_error(self: 'AppPageController'):
    return self.get_html(self.cur_func_name(), template_name="_text_error.html", text=self.text_error)


@hotwire_html_template_element()
def incl_select_orig_lang(self: 'AppPageController'):
    return self.get_html(self.cur_func_name(), template_name="_select_orig_lang.html",
                         supported_langs=self.supported_langs,
                         orig_lang=self.orig_lang,
                         enable_orig_lang_change=self.enable_orig_lang_change)


@hotwire_html_template_element()
def incl_makeit(self: 'AppPageController'):
    return self.get_html(self.cur_func_name(), template_name="_makeit.html",
                         making_error=self.making_error,
                         disable_makeit_button=bool(self.cur_makeit_worker),
                         download_file_name=self.download_file_name,
                         download_as_name=self.download_as_name)


@hotwire_html_template_element()
def incl_select_voices(self: 'AppPageController'):
    return self.get_html(self.cur_func_name(), template_name="_select_voices.html",
                         present_langs=self.present_langs(),
                         voices=self.voices)


@hotwire_html_template_element()
def incl_add_translation(self: 'AppPageController'):
    return self.get_html(self.cur_func_name(), template_name="_add_translation.html",
                         supported_langs=self.supported_langs,
                         present_langs=self.present_langs(),
                         translation_message=self.message,
                         disabled=bool(self.cur_translate_worker) or bool(self.cur_makeit_worker))


@hotwire_html_template_element()
def incl_line_player(self: 'AppPageController'):
    return self.get_html(self.cur_func_name(), template_name="_line_player.html",
                         file_name_mp3=self.file_name_mp3)


@hotwire_html_template_element()
def incl_makeit_progress_indicator(self: 'AppPageController'):
    if self.cur_makeit_worker:
        template = """
                    <div>
                    <label>{{ stage }} {{ cur_progress }}%</label><progress value='{{ cur_progress }}' max='100'>
                    </progress>
                    <input type="submit" name="terminate" value="Cancel">
                    </div>
                    """

        stage = self._worker.get_stage(self.cur_makeit_worker)
        return self.get_html(self.cur_func_name(),
                             string_template=template,
                             cur_progress=round(self.cur_makeit_progress),
                             stage=stage)
    else:
        return self.get_html(self.cur_func_name(), string_template="")


@hotwire_html_template_element()
def incl_translate_progress_indicator(self: 'AppPageController'):
    if self.cur_translate_worker:
        template = """
                    <div>
                    <label>{{ stage }} {{ cur_progress }}%</label><progress value='{{ cur_progress }}' max='100'>
                    </progress>
                    <input type="submit" name="terminate_translate" value="Cancel">
                    </div>
                    """
        stage = self._worker.get_stage(self.cur_translate_worker)
        return self.get_html(self.cur_func_name(),
                             string_template=template,
                             cur_progress=round(self.cur_translate_progress),
                             stage=stage)
    else:
        return self.get_html(self.cur_func_name(), string_template="")


@hotwire_html_template_element()
def incl_refresh_makeit_status(self: 'AppPageController'):
    if self.cur_makeit_worker or self.cur_translate_worker:
        return self.get_html(self.cur_func_name(),
                             string_template=self.initiate_timed_updates_template("refresh_makeit_status", 1000))

    return self.get_html(self.cur_func_name(), string_template="")


@hotwire_html_template_element()
def incl_navigation_bar(self: 'AppPageController'):
    template = """
        <div class="navbar">
            <h1>Multilingual voice and subtitles over video</h1>
            {% if user_id is none %}
            <div class="navbar-buttons">
                <a href="{{ url_for('login') }}" data-turbo="false">Log in</a>
                <a href="{{ url_for('register') }}" data-turbo="false">Sign up</a>
            </div>
            {% else %}
            <div>
                <h4>Tokens: 10000</h4>
            </div>
            <div>
                <h3>{{ user_id }}</h3>
                <a href="{{ url_for('logout') }}" data-turbo="false">Sign out</a>
            </div>
            {% endif %}
        </div>
    """
    return self.get_html(self.cur_func_name(), string_template=template, user_id=self.user_id)
