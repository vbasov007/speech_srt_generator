from dataclasses import dataclass
from typing import List, Optional
from utils import string_to_ms


@dataclass
class ScriptLine:
    type: str
    value: str = ''
    time_to_next: int = 0
    adjustment: int = 0
    absolute_start_time: int = 0

    def __str__(self):
        return f'{self.type}: {self.value} ({self.time_to_next}ms, {self.adjustment}ms)'


def text2lines(text, sentence_prefix=None, break_prefix="#") -> List[ScriptLine]:
    res = []
    lines = text.split('\n')
    for line in lines:
        if len(line.strip()) == 0:
            continue
        if line.startswith(break_prefix):
            value = line[1:].strip()
            if value.isnumeric():
                res.append(ScriptLine('break', time_to_next=int(value)))
            elif string_to_ms(value) is not None:
                res.append(ScriptLine('time_mark', absolute_start_time=string_to_ms(value)))
            continue

        if sentence_prefix is None:
            line = line.strip()
        elif line.startswith(sentence_prefix):
            line = line[len(sentence_prefix):].strip()
        else:
            continue
        res.append(ScriptLine('sentence', line, 0, 0))

    return res


def lines2ssml(lines: List[ScriptLine]) -> str:
    res = ''
    for line in lines:
        if line.type == 'break':
            res += f'<break time="{line.time_to_next}ms"/>\n'
            continue

        if line.type == 'time_mark':
            if line.adjustment > 0:
                adj = line.adjustment - 380
                if adj < 0:
                    adj = 0
                while adj > 10000:
                    res += f'<break time="10000ms"/>\n'
                    adj -= 10000
                res += f'<break time="{adj}ms"/>\n'
            continue

        # res += f'<s>{line.value}</s>\n'
        if line.adjustment > 0:
            res += f'<s>{line.value}<break time="{line.adjustment}ms"/></s>\n'
        else:
            res += f'<s>{line.value}</s>\n'

    # return f'<speak>{res}</speak>'
    return res


def get_line_by_pos(text: str, pos) -> Optional[str]:
    lines = text.split("\n")
    current_pos = 0
    for line in lines:
        if current_pos + len(line) >= pos:
            return line
        else:
            current_pos += len(line) + 1  # +1 for the '\n' character
    return None
