from typing import List

from multilang import Translation
from utils import string_to_ms


def add_translation(text, target_lang, source_lang, url, key, startswith_symb="#", block_visual_splitter="---",
                    verify_cert=True,
                     report_progress = None) -> str:
    lines = text.split('\n')
    # url, key = translator_url_key()
    tr = Translation(url, key, verify=verify_cert)
    res = []
    for count, line in enumerate(lines):

        if report_progress:
            report_progress(100*count/len(lines), "Please, wait... translating")

        # leave visual splitter between blocks
        if line.strip() == block_visual_splitter:
            # res.append(line)
            continue

        # leave empty lines empty
        if len(line.strip()) == 0:
            res.append("")
            continue

        source_lang_prefix = f"{startswith_symb}{source_lang}: "

        # leave pause markers untouched (e.g. #1000) and add visual splitter before them for better readability
        if line.startswith(startswith_symb):
            val = line[len(startswith_symb):]
            if val.strip().isnumeric() or (string_to_ms(val) is not None):
                res.append(block_visual_splitter)
                res.append(line)
                continue
            if not line.startswith(source_lang_prefix):
                res.append(line)
                continue

        # clear source_lang prefix from non-empty lines
        source_lang_prefix = f"{startswith_symb}{source_lang}: "
        if line.startswith(source_lang_prefix):
            line = line[len(source_lang_prefix):]

        # if non-empty line doesn't start with startswith_symb, then consider it as source_lang text
        prefixed_line = line
        if not line.startswith(startswith_symb):
            prefixed_line = source_lang_prefix + line

        # translate prefixed_line to  target_lang
        if prefixed_line.startswith(source_lang_prefix):
            prev_line = res[-1] if len(res) > 0 else None
            if prev_line != block_visual_splitter:
                res.append(block_visual_splitter)
            res.append(prefixed_line)
            output_line = f"{startswith_symb}{target_lang}: " + tr.translate_text(line, target_lang, source_lang)
            res.append(output_line)

    return '\n'.join(res)


def present_translations(text, startswith_symb="#") -> List[str]:
    import re
    pattern = r'^' + re.escape(startswith_symb) + r'([A-Za-z]{2}):'
    matches = re.findall(pattern, text, re.MULTILINE)
    return list(set(matches))


def split_translations(text, orig_lang, langs: list, startswith_symb="#", block_visual_splitter="---",
                       ignore_codes=False) -> dict:
    res = {}
    langs = list(set([orig_lang, ] + langs))
    lang_lines = {key: [] for key in langs}

    lines = text.split('\n')
    for line in lines:
        # ignore visual splitter between blocks
        if line.startswith(block_visual_splitter):
            continue

        # add empty lines to all languages
        if len(line.strip()) == 0:
            for key in lang_lines.keys():
                lang_lines[key].append("")
            continue

        # add pause markers end time markers to all languages
        if line.startswith(startswith_symb):
            val = line[len(startswith_symb):]
            if (val.strip().isnumeric() or (string_to_ms(val) is not None)) and not ignore_codes:
                for key in lang_lines.keys():
                    lang_lines[key].append(line)
                continue

        # add non-empty line to default language if no prefix
        if not line.startswith(startswith_symb):
            lang_lines[orig_lang].append(line)
            continue

        # add line to lang if prefix
        for key in lang_lines.keys():
            lang_prefix = f"{startswith_symb}{key}:"
            if line.startswith(lang_prefix):
                lang_lines[key].append(line[len(lang_prefix):].strip())
                break

    lang_lines = {key: text for key, text in lang_lines.items() if text}

    # transform to result dict with values as strings
    for key in lang_lines.keys():
        res[key] = '\n'.join(lang_lines[key])

    return res
