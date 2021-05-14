import datetime as dt


def text_to_ssml(text: str, speech_style: str = None) -> str:
    """
    Convert plain text to SSML (Speech Synthesis Markup Language.
    Each text line is placed inside the <s> (sentence) tag
    Line of the form '#1000' means a pause of 1000ms
    SSML details: https://docs.aws.amazon.com/polly/latest/dg/ssml.html
    :param text: str input plain text
    :param speech_style: 'conversational' or 'news'
    :return: str SSML text
    """

    lines = text.split('\n')

    res = ''
    for line in lines:
        if line.startswith('#'):
            res += f'<break time="{line[1:]}ms"/>\n'
        else:
            if (len(line) > 1) and not line.isspace():
                res += f'<s>{line}</s>\n'

    if speech_style:
        res = f'<amazon:domain name="{speech_style}">{res}</amazon:domain>'

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
