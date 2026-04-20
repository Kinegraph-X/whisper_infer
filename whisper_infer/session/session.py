from dataclasses import dataclass
from whisper_infer.states import SessionState
from whisper_infer.pipeline import Pipeline, PipelineFailure

@dataclass
class Session:
    id: str                          # UUID
    media_path: str
    keywords: list[str]
    started_at: float
    pipelines: list[Pipeline]
    state: SessionState.PENDING
    failure_reasons: list[PipelineFailure]  # pipeline_id + raison + timestamp