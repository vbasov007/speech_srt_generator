from abc import ABC, abstractmethod

from typing import Optional

from .output_chunk import SpeechChunk


class SpeechSynthInterface(ABC):

    @abstractmethod
    def synth(self, text: str,
              voice: str = "default",
              speech_style: str = "default",
              language_code: str = "default",
              text_type: str = "ssml",
              encoding: str = "LINEAR16",
              sample_rate_hz: Optional[int] = None,
              absolute_start_time_ms: Optional[int] = None) -> SpeechChunk:
        pass
