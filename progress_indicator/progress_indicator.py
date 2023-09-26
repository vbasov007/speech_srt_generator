from flask import render_template


class ProgressIndicator:

    def __init__(self, target, app, turbo, template):
        self._target = target
        self._app = app
        self._turbo = turbo
        self._template = template
        self._enable = True

    def message(self, progress_info: dict):
        if self._enable:
            with self._app.app_context():
                print(progress_info)
                self._turbo.push(self._turbo.replace(render_template(self._template, progress_info=progress_info),
                                                     self._target))

    def clear(self):
        self.message({})