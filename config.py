from dotenv import load_dotenv
from typing import List, Pattern, Match
import os
from dataclasses import dataclass

load_dotenv()

@dataclass
class config():
    USE_MOCK : bool = False
    USE_TEST : bool = False
    should_match : bool = True # default overriden in args_parser
    keywords : List[str] | None = None
    media_path : str = ""
    channel_name : str = ""
    whisper_path = "whisper_infer.py" # default overriden in args_parser
    segment_duration = os.get_env('segment_duration', 3600)
    log_level = os.getenv("LOG_LEVEL", "INFO")
    whisper_model = os.getenv("WHISPER_MODEL", "small")