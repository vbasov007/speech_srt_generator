from flask import render_template
from websynth import turbo

def generic_update(template_or_content: str, target: str, render: bool = True, **kwargs):
    content=template_or_content
    if render:
        content = render_template(template_or_content, **kwargs)
    return turbo.update(content, target)
