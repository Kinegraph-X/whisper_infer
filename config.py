from typing import List, Pattern, Match
from dataclasses import dataclass

@dataclass
class config():
    USE_MOCK : bool = False
    USE_TEST : bool = False
    should_match : bool = True
    keywords : List[str] | None = None
    keywords_pattern : Pattern | None = None
    channel_name : str = ""
    whisper_path = "whisper_infer.py"
    segment_duration = 3600