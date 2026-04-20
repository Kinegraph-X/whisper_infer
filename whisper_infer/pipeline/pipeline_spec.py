from uuid import uuid4
from typing import List
from dataclasses import dataclass
from whisper_infer.tasks import Task
from pipeline_state import PipelineState

@dataclass
class PipelineSpec():
        id : str = uuid4()
