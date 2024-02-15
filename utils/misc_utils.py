import datetime as dt
import re
from typing import Optional


def split(delimiters, string, maxsplit=0):
    regex_pattern = '|'.join(map(re.escape, delimiters))
    return re.split(regex_pattern, string, maxsplit)


def set_lang(text, lc):
    return f'<lang xml:lang="{lc}"><s>{text}</s></lang>'


def is_cyr(text):
    return bool(re.search('[а-яА-Я]', text))


def say_ru_if_cyr(text):
    if is_cyr(text):
        return f'<lang xml:lang="ru-RU">{text}</lang>'

    return text


def text_to_ssml(text: str, speech_style: str = None, repeat_delay_ms_per_symb=100) -> str:
    res = ''
    lines = text.split('\n')
    for line in lines:

        if line.startswith('#'):
            break_time = line[1:].strip()

            if break_time.isnumeric():
                res += f'<break time="{break_time}ms"/>\n'
                continue
            continue

        res += f'<s>{say_ru_if_cyr(line)}</s>\n'
    # return f'<speak>{res}</speak>'
    return res

def tf(delta_ms: int) -> str:
    """
    Returns formatted time e.g. 00:01:30,123
    :param delta_ms:
    :return:
    """
    tz = dt.datetime.strptime("0", '%S')
    delta = dt.timedelta(milliseconds=delta_ms)
    return (tz + delta).strftime("%H:%M:%S,%f")[:-3]


def string_to_ms(time_str: str) -> Optional[int]:
    time_str = time_str.strip()
    sep = ":"
    p = time_str.split(sep)
    if len(p) == 3:
        h, m, s = p
    elif len(p) == 2:
        m, s = p
        h = "0"
    else:
        return None

    s = s.replace(',', '.')
    try:
        sf = float(s)
    except ValueError:
        return None

    if h.isnumeric() and m.isnumeric():
        return int(int(h) * 3600000 + int(m) * 60000 + sf * 1000)

    return None


def speech_marks_to_srt(speech_marks: list, remove_tags=True) -> str:
    """
    Convert speech marks to SRT subtitles
    The speech marks is a list of dict: [{'time': TIME_MS, 'type': 'sentence', 'value': SOME_TEXT}, {...},..]
    :param speech_marks: list of dict
    :return: SubRip .SRT subtitles for entire text as str
    """

    res = ""
    for index, sm in enumerate(speech_marks):
        if sm['type'] != 'sentence':
            continue
        cur_text = sm['value']
        cur_time = sm['time']
        next_sentence_start = speech_marks[index + 1]['time'] if len(speech_marks) > (index + 1) else (cur_time + 60000)
        end_time = min(next_sentence_start, cur_time + 70 * len(cur_text))

        res += str(index + 1) + '\n'
        res += f'{tf(cur_time)} --> {tf(end_time)}\n'
        cur_text = remove_all_tags(cur_text) if remove_tags else cur_text
        res += cur_text + '\n\n'

    return res


def remove_all_tags(text):
    # Define regex pattern to match HTML tags
    pattern = re.compile(r'<.*?>')

    # Remove HTML tags using the pattern
    filtered_text = re.sub(pattern, '', text)

    return filtered_text
