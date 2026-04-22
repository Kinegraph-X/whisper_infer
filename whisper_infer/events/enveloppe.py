from dataclasses import dataclass
from .msg_event import LogEvent
from whisper_infer.session import SessionSnapshot

@dataclass
class Enveloppe:
    event : LogEvent
    pipeline_state : SessionSnapshot