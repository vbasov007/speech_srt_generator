from dataclasses import dataclass
from typing import List


@dataclass
class ScriptLine:
    type: str
    value: str = ''
    duration: int = 0
    adjustment: int = 0

    def __str__(self):
        return f'{self.type}: {self.value} ({self.duration}ms, {self.adjustment}ms)'


def text2lines(text, sentence_prefix=None, break_prefix="#") -> List[ScriptLine]:
    res = []
    lines = text.split('\n')
    for line in lines:
        if len(line.strip()) == 0:
            continue
        if line.startswith(break_prefix):
            break_time = line[1:].strip()
            if break_time.isnumeric():
                res.append(ScriptLine('break', duration=break_time))
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
            res += f'<break time="{line.duration}ms"/>\n'
            continue

        # res += f'<s>{line.value}</s>\n'
        if line.adjustment > 0:
            res += f'<s>{line.value}<break time="{line.adjustment}ms"/></s>\n'
        else:
            res += f'<s>{line.value}</s>\n'

    return f'<speak>{res}</speak>'
