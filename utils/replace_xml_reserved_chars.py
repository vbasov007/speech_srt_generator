# import re
#
#
# def replace_text(text, old_substr, new_substr):
#     ssml_tags = re.findall(r'<[^>]*?>.*?</[^>]*?>', text)
#
#     # get indexes of SSML tags
#     tag_indexes = [(m.start(), m.end()) for m in re.finditer(r'<[^>]*?>.*?</[^>]*?>', text)]
#
#     start = 0
#     new_text = ""
#     for indexes in tag_indexes:
#         new_text += text[start:indexes[0]].replace(old_substr, new_substr) + text[indexes[0]:indexes[1]]
#         start = indexes[1]
#
#     new_text += text[start:].replace(old_substr, new_substr)
#
#     return new_text
#
#
# def replace_xml_reserved_chars(text):
#     text = replace_text(text, "&", "&amp;")
#     text = replace_text(text, "%", "&#37;")
#     text = replace_text(text, ">", "&gt;")
#     text = replace_text(text, "<", "&lt;")
#     return text

import html
import re


def escape_xml_reserved_chars(text):
    # identifying SSML tags
    ssml_tags = re.findall(r'<[^>]*?>.*?</[^>]*?>', text)

    # get indexes of SSML tags
    tag_indexes = [(m.start(), m.end()) for m in re.finditer(r'<[^>]*?>.*?</[^>]*?>', text)]

    start = 0
    new_text = ""
    for indexes in tag_indexes:
        new_text += html.escape(text[start:indexes[0]]) + text[indexes[0]:indexes[1]]
        start = indexes[1]
    new_text += html.escape(text[start:])

    return new_text

def unescape_xml_chars(text):
    return html.unescape(text)