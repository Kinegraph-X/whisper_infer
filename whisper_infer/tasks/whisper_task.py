from dataclasses import dataclass
from typing import List
from whisper_infer.utils import StrSerializable

@dataclass
class WhisperTask:
    command : List[str | StrSerializable]
    transcript_file : str
    start_timestamp : str