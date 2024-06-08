from typing import Optional
from dataclasses import dataclass


@dataclass
class SpeechChunk:
    stream: bytes
    subtitle: str
    source_text: str
    language_code: str
    absolut_start_time_ms: Optional[int]
    duration_ms: int
    sample_rate_hz: int
    encoding: str
