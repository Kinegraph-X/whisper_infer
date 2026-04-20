from dataclasses import dataclass
from uuid import uuid4

@dataclass
class PipelineFailure:
    pipeline_id : uuid4
    reason : str
    timestamp : float