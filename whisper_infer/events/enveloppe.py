from dataclasses import dataclass
from msg_event import LogEvent
from whisper_infer.pipeline import PipelineState

@dataclass
class Enveloppe:
    event : LogEvent
    pipeline_state : PipelineState