from dataclasses import dataclass
from whisper_infer.states import TaskState

@dataclass
class TaskSnapshot:
    name: str
    state: TaskState
    started_at: float
    elapsed: float
    last_error: str
    retries: int
    progress: dict  # extensible : {"lines_processed": 42, ...}