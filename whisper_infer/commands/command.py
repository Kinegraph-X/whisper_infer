from typing import List, Tuple, Dict, Sequence
from dataclasses import dataclass

from whisper_infer.utils import StrSerializable

@dataclass
class FFMpegCommand:
    audio_filepath : str
    cmd : list[str | StrSerializable]
    worker_name : str
    transcript_filename : str