import datetime as dt
import re


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
    return f'<speak>{res}</speak>'


def tf(delta_ms: int) -> str:
    """
    Returns formatted time e.g. 00:01:30,123
    :param delta_ms:
    :return:
    """
    tz = dt.datetime.strptime("0", '%S')
    delta = dt.timedelta(milliseconds=delta_ms)
    return (tz + delta).strftime("%H:%M:%S,%f")[:-3]


def speech_marks_to_srt(speech_marks: list) -> str:
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
        res += cur_text + '\n\n'

    return res


