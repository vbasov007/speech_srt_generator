import inspect
import json
from dataclasses import dataclass
from typing import Callable, Any, Dict, Union

from flask import render_template, render_template_string


@dataclass
class HotFunc:
    name: str
    func: Callable
    freeze: Any = None
    update_always: bool = False
    for_full_render_only: bool = False


class HotwirePage:

    def __init__(self, turbo, request_obj, session_obj=None):
        self._request = request_obj
        self._turbo = turbo
        self._session = session_obj
        self.main_template = ""
        self.registry: Dict[str, HotFunc] = {}
        self._context_var_names: set = set()
        self._session_var_names: set = set()
        self._class_name = self.__class__.__name__.lower()

        self.register(self.embedded_context_frame, update_always=True)

    def get_request_form_value(self, element_id):
        return self._request.form.get(element_id)

    def add_to_stored_context(self, variable_name_or_list: Union[str, list]):
        self._context_var_names.update(self._add_context(variable_name_or_list))

    def add_to_session_context(self, variable_name_or_list: Union[str, list]):
        self._session_var_names.update(self._add_context(variable_name_or_list))

    def _add_context(self, variable_name_or_list: Union[str, list]) -> set:
        res = set()
        if not isinstance(variable_name_or_list, list):
            variable_name_or_list = [variable_name_or_list, ]
        for variable_name in variable_name_or_list:
            if not hasattr(self, variable_name):
                raise ValueError(f"{variable_name} is not defined before attempt to store")
            res.add(variable_name)

        return res

    def register(self, func, update_always=False, for_full_render_only=False):
        self.registry.update({func.__name__: HotFunc(func.__name__, func,
                                                     update_always=update_always,
                                                     for_full_render_only=for_full_render_only)})
        return func

    def get_registry(self, func):
        return self.registry.get(func.__name__)

    @staticmethod
    def cur_func_name():
        return inspect.currentframe().f_back.f_code.co_name

    def _hotwire_frame_id(self, hotfunc: HotFunc):
        return f"{hotfunc.name}-{self._class_name}"

    def wrap_turbo_frame(self, hf: HotFunc, template_name=None, string_template=None, **template_args):
        if template_name is not None:
            res = render_template(template_name, **template_args)
        else:
            if string_template is not None:
                res = render_template_string(string_template, **template_args)
            else:
                res = f'{template_args}'
        res = f'<turbo-frame id="{self._hotwire_frame_id(hf)}">{res}</turbo-frame>'
        return res

    def freeze(self):
        for hf in self.registry.values():
            hf.freeze = hf.func()

    def full_render(self):
        self._save_session_context()
        return render_template(self.main_template, page=self)

    def update(self):
        self._save_session_context()
        stream = []
        for hf in self.registry.values():
            if not hf.for_full_render_only:
                html = hf.func()
                if (hf.freeze != html) or hf.update_always:
                    stream.append(self._turbo.replace(html, target=self._hotwire_frame_id(hf)))
        return self._turbo.stream(stream)

    def get_html(self, hf: Union[HotFunc, str], template_name=None, string_template=None, **template_args):
        if isinstance(hf, str):
            hot_func = self.registry[hf]
        else:
            hot_func = hf
        return self.wrap_turbo_frame(hot_func, template_name, string_template, **template_args)

    @staticmethod
    def context_frame_template():
        return '<input type="hidden" name="context_frame" value="{{ context_string }}">'

    def embedded_context_frame(self):
        res: dict = {}
        for var_name in self._context_var_names:
            res[var_name] = getattr(self, var_name)
        return self.get_html(self.cur_func_name(), string_template=self.context_frame_template(),
                             context_string=json.dumps(res))

    def restore_context(self):
        self._restore_embedded_context()
        self._restore_session_context()

    def _restore_embedded_context(self):
        updated_data = json.loads(self._request.form.get("context_frame"))
        for key, value in updated_data.items():
            if key in self._context_var_names:
                setattr(self, key, value)

    def _restore_session_context(self):
        if self._session is None:
            return
        for key, value in self._session.items():
            if key in self._session_var_names:
                setattr(self, key, value)

    def _save_session_context(self):
        if self._session is None:
            return
        for var_name in self._session_var_names:
            self._session[var_name] = getattr(self, var_name)

    @staticmethod
    def initiate_timed_updates_template(html_element_name: str, interval_ms: int) -> str:
        template = f"""
        <script>
        if (typeof hwIntervalObject_{html_element_name} !== 'undefined') {{
            clearInterval(hwIntervalObject_{html_element_name})
        }}
        var hwIntervalObject_{html_element_name} = setInterval(function() {{
                const hwRefreshButton_{html_element_name} = document.querySelector('input[name="{html_element_name}"]');
                if(hwRefreshButton_{html_element_name} ) hwRefreshButton_{html_element_name}.click();
        }}, {interval_ms});
        </script>
        <input type="submit" name="{html_element_name}" value="_" hidden>
        """
        return template
