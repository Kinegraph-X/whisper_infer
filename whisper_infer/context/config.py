from dotenv import load_dotenv
from typing import List
import os
from dataclasses import dataclass

load_dotenv()

@dataclass
class Config():
    USE_MOCK : bool = False
    USE_TEST : bool = False
    debug : bool = False
    dist : bool = False
    should_match : bool = True # default overriden in args_parser
    keywords : List[str] | None = None
    media_path : str = "https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/tears-of-steel-audio_eng=128002-video_eng=1001000.m3u8"
    channel_name : str = ""
    vod_uid : str = ""
    whisper_path = "whisper_infer.py" # default overriden in args_parser
    whisper_func = 'export_transcription'
    segment_duration = os.getenv('segment_duration', 3600)
    log_level = os.getenv("LOG_LEVEL", "INFO")
    whisper_model = os.getenv("WHISPER_MODEL", "small")
    whisper_platform = os.getenv("WHISPER_PLATFORM", "cpu")
    whisper_compute_type = "int8" if os.getenv("WHISPER_PLATFOM") == "cpu" else 'FP16'

config = Config()