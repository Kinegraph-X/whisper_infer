from dataclasses import dataclass
from enum import Enum
import threading

class PipelineState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"

@dataclass
class PipelineStatus():
    global_duration = 0
    still_to_transcribe = []
    ffmpeg_done_event = threading.Event()
    matches = []