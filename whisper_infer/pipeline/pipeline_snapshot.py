from dataclasses import dataclass
from whisper_infer.tasks import TaskSnapshot

@dataclass  
class PipelineSnapshot:
    tasks: dict[str, TaskSnapshot]
    early_exit: bool
    started_at: float
    elapsed: float