from typing import List, Dict
from dataclasses import dataclass
from whisper_infer.states import SessionState
from whisper_infer.pipeline import Pipeline, PipelineFailure

@dataclass
class SessionSnapshot:
    id : str
    media_path : str
    keywords : List[str]
    state : SessionState
    started_at : float
    elapsed : float
    pipelines : Dict[str, Pipeline]
    failure_reasons : List[PipelineFailure]