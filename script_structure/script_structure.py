from dataclasses import dataclass, field, is_dataclass, asdict
from typing import Optional, List, Dict


@dataclass
class ScriptSection:
    start_time: Optional[int] = None
    pause: Optional[int] = None
    translation: dict = field(default_factory=dict)
    voice: dict = field(default_factory=dict)
    source_lang: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> 'ScriptSection':
        return cls(**data)

    def asdict(self) -> dict:
        if is_dataclass(self):
            return asdict(self)
        return self.__dict__


class MultilangSpeechScript:

    def __init__(self, list_of_dicts: Optional[List[Dict]] = None):
        self._data: List[ScriptSection] = []
        if list_of_dicts is not None:
            self._data = [ScriptSection.from_dict(d) for d in list_of_dicts]

    def from_text(self, text):
        return []

    def split_section(self, section_index, splitter: str):
        pass

    def set_start_time(self, section_index, start_time):
        self.script[section_index].start_time = start_time
