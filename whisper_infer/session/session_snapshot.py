from typing import List
from dataclasses import dataclass
from whisper_infer.states import SessionState
from whisper_infer.pipeline import Pipeline, PipelineFailure

class SessionSnapshot:
    session_id : str
    media_path : str
    keywords : List[str]
    state : SessionState
    started_at : float
    elapsed : float
    pipelines : List[Pipeline]
    failure_reasons : List[PipelineFailure]