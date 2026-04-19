from typing import List
from dataclasses import dataclass
from whisper_infer.tasks import Task
from pipeline_state import PipelineState

class Pipeline():
    def __init__(self, tasks : List[Task]):
        self.tasks : List[Task] = tasks
        self.state : PipelineState = PipelineState.PENDING
        self.currently_running : Task
        self.started_at : str
        self.early_exit : bool = False