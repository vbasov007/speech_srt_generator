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

def text_to_ssml_advanced(text: str, speech_style: str = None, repeat_delay_ms_per_symb = 100) -> str:
    lang_names = {
        'ru': 'ru-RU',
        'en': 'en-EN'
    }

    res = ''
    special_mode = ''
    lines = text.split('\n')
    for line in lines:

        if line.startswith('#'):
            com = line[1:]

            if com.isnumeric():
                res += f'<break time="{line[1:]}ms"/>\n'
                continue

            special_mode = ''
            if com in ('rw', 'rp', 'dt', 'rt'):
                special_mode = com
                continue

            continue

        if not special_mode:
            res += f'<s>{say_ru_if_cyr(line)}</s>\n'

        if special_mode == 'rw':
            words = split(('.', ',', ';', '\n'), line)
            words = [w.strip() for w in words]
            for word in words:
                res += f'<s>{say_ru_if_cyr(word)}</s>\n'
                res += f'<break time="{len(word) * repeat_delay_ms_per_symb}ms"/>\n'
        if special_mode == 'rp':
            res += f'<s>{say_ru_if_cyr(line)}</s>\n'
            res += f'<break time="{len(line) * repeat_delay_ms_per_symb}ms"/>\n'

        if special_mode in ('dt', 'rt'):
            pair = line.split('>')
            print(pair)
            if len(pair) != 2:
                print(f'"{line}" doesnt work in translation mode')
                continue
            first, second = pair
            first=first.strip()
            second=second.strip()

            if special_mode == 'rt':
                first, second = second, first

            res += f'<s>{say_ru_if_cyr(first)}</s>\n'
            res += f'<break time="{len(second) * repeat_delay_ms_per_symb}ms"/>\n'
            res += f'{say_ru_if_cyr(second)}\n'
            res += f'<break time="{len(second) * repeat_delay_ms_per_symb*2}ms"/>\n'

    return f'<speak>{res}</speak>'

def text_to_ssml(text: str, speech_style: str = None, special_mode = '', repeat_delay_ms_per_symb = 100) -> str:
    """
    Convert plain text to SSML (Speech Synthesis Markup Language.
    Each text line is placed inside the <s> (sentence) tag
    Line of the form '#1000' means a pause of 1000ms
    SSML details: https://docs.aws.amazon.com/polly/latest/dg/ssml.html
    :param text: str input plain text
    :param speech_style: 'conversational' or 'news'
    :return: str SSML text
    """
    res = ''
    lines = text.split('\n')
    words = split(('.', ',', ';', '\n'), text)
    if speech_style:
        res = f'<amazon:domain name="{speech_style}">{res}</amazon:domain>'

    if not special_mode:

        for line in lines:
            if line.startswith('#'):
                res += f'<break time="{line[1:]}ms"/>\n'
            else:
                if (len(line) > 1) and not line.isspace():
                    res += f'<s>{line}</s>\n'

    else:
        if special_mode == 'phrase_repetition':
            items = lines
        elif special_mode == 'word_repetition':
            items = words
        else:
            raise ValueError(f'Unknown special_mode {special_mode}')

        for item in items:
            res += f'<s>{item}</s>\n'
            res += f'<break time="{len(item)*repeat_delay_ms_per_symb}ms"/>\n'

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
