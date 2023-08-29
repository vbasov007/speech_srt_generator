from dataclasses import dataclass

@dataclass
class Sentence:
    start_time_ms: int
    delay_after_ms: int
    adjustment_ms: int
    text: str

class Script2ssml:

    def __init__(self, script: str):
        self._script = script
        self._sentences = []

    def rebuild(self):
        pass

    def as_ssml(self) -> str:
        pass

    def get_start_time(self, sentence_index) -> int:
        pass

    def set_start_time(self, sentence_index, start_time_ms: int):
        pass

    def get_sentence(self, sentence_index: int) -> str:
        pass

    def set_sentence(self, sentence_index: int, sentence: str):
        pass

    def sentence_count(self) -> int:
        pass
